"""
Turns each awesome-list entry into a card with the linked page's preview image and favicon.
The options and the markup the theme styles are in hooks/README.md.
"""

import io
import logging
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as etree
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs.config import config_options
from mkdocs.config.base import LegacyConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.utils import get_relative_url
from PIL import Image
from webpreview import web_preview

log = logging.getLogger("mkdocs.hooks.awesome_list")

CONFIG_SCHEME = (
    ("debug-log", config_options.Type(bool, default=False)),
    ("default-style", config_options.Type(str, default="media")),
    ("section-styles", config_options.Type(dict, default={})),
)

# A top-level item starting with a web link; image links (badges) and in-page links aren't entries
ENTRY_RE = re.compile(r"^- \[(?!!)(.*?)\]\(\s*(https?://[^)\s]+)\s*\)", re.MULTILINE)
ASSETS_DIR = "assets/awesome-list"
CSS_FILE = "awesome-list.css"
FAVICON_URL = "https://www.google.com/s2/favicons?domain={host}&sz=64"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; mkdocs-awesomelist)"}
# Enough for Pillow to read the dimensions; images with bigger headers aren't logos anyway
IMAGE_PROBE_BYTES = 64 * 1024
CODE_HOSTS = ("github.com", "gitlab.com")


@dataclass
class Preview:
    image: Optional[str] = None
    # "picture", "logo" or "none"; tells the theme how to frame the image
    image_kind: str = "none"


def _resolve_image_url(image, page_url):
    """Return the image as an absolute URL, or None."""
    if not image:
        return None
    if image.startswith("//"):
        return "https:" + image
    return urljoin(page_url, image)


def _image_kind(width, height):
    """Small images are logos, shown at their own size; anything else is a picture."""
    return "logo" if max(width, height) <= 200 else "picture"


def _get_image(image_url):
    """Stream an image, backing off when rate limited (GitHub's OG images often are)."""
    for delay in (1, 2, 4):
        resp = requests.get(image_url, timeout=10, stream=True, headers=HEADERS)
        if resp.status_code != 429:
            return resp
        resp.close()
        time.sleep(delay)
    return requests.get(image_url, timeout=10, stream=True, headers=HEADERS)


def _probe_image(image_url):
    """Return the image kind, or None if it can't be loaded."""
    try:
        with _get_image(image_url) as resp:
            if resp.status_code >= 400:
                print(f"\n  WARNING: Image returned {resp.status_code}: {image_url}")
                return None
            content_type = resp.headers.get("Content-Type", "")
            data = resp.raw.read(IMAGE_PROBE_BYTES, decode_content=True)
    except Exception as e:
        print(f"\n  WARNING: Could not reach image: {image_url} ({e})")
        return None
    if not data:
        print(f"\n  WARNING: Empty image: {image_url}")
        return None
    if "svg" in content_type:
        # Browsers won't render a broken SVG, and some sites serve one
        if not data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
            print(f"\n  WARNING: Invalid SVG image: {image_url}")
            return None
        return "logo"
    try:
        with Image.open(io.BytesIO(data)) as img:
            return _image_kind(*img.size)
    except Exception:
        # Pillow can't read every format a browser can (e.g. AVIF)
        return "picture" if content_type.startswith("image/") else None


def _fetch_preview(url):
    """Fetch the OpenGraph image of a page and work out how to frame it."""
    try:
        _title, _description, image = web_preview(url, timeout=10)
        image = _resolve_image_url(image, url)
    except Exception as e:
        print(f"\n[AwesomeList] Error fetching preview for {url}: {e}")
        return Preview()
    kind = _probe_image(image) if image else None
    return Preview(image, kind) if kind else Preview()


def _fetch_favicon(host):
    """Return the site's favicon as PNG bytes, or None."""
    try:
        resp = requests.get(FAVICON_URL.format(host=host), timeout=10, headers=HEADERS)
    except Exception:
        return None
    # The service answers 404 with a generic globe when a site has no favicon
    if resp.status_code >= 400 or not resp.content:
        return None
    return resp.content


def _host(url):
    host = urlparse(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


def _domain_label(url):
    """Host without "www.", plus the owner for code-hosting sites."""
    host = _host(url)
    if host in CODE_HOSTS:
        owner = urlparse(url).path.strip("/").split("/")[0]
        if owner:
            return f"{host}/{owner}"
    return host


def _favicon_filename(host):
    return re.sub(r"[^a-z0-9.-]", "_", host.lower()) + ".png"


def _add_class(element, name):
    classes = element.get("class")
    element.set("class", f"{classes} {name}" if classes else name)


def _entry_link(li):
    """The link an item starts with, unless it's an image link (a badge), or None."""
    container = li
    # Loose lists (blank lines between items) wrap each item's text in a <p>
    if len(li) and li[0].tag == "p" and not (li.text or "").strip():
        container = li[0]
    if (container.text or "").strip() or not len(container):
        return None
    link = container[0]
    if link.tag != "a" or (not (link.text or "").strip() and len(link) and link[0].tag == "img"):
        return None
    return link


def _unwrap_paragraph(li):
    if len(li) and li[0].tag == "p" and not (li.text or "").strip():
        p = li[0]
        li.remove(p)
        li.text = p.text
        for i, child in enumerate(p):
            li.insert(i, child)


def _wrap_description(li, css_class):
    """Move what follows `<a>Name</a>` into a span, up to any nested list."""
    link = li[0]
    tail = link.tail or ""
    desc = etree.Element("span", {"class": css_class})
    desc.text = tail[3:] if tail.startswith(" - ") else tail.lstrip()
    link.tail = None
    for child in list(li)[1:]:
        if child.tag in ("ul", "ol"):
            break
        li.remove(child)
        desc.append(child)
    # The description is optional
    if desc.text.strip() or len(desc):
        li.insert(1, desc)
    return desc


def _plain_text(element):
    """Text content with Python-Markdown's inline placeholders resolved or dropped."""
    text = "".join(element.itertext())
    text = re.sub("\x02(\\d+)\x03", lambda m: chr(int(m.group(1))), text)
    return re.sub("\x02.*?\x03", "", text).strip()


class _EntryTreeprocessor(Treeprocessor):
    def __init__(self, md, plugin):
        super().__init__(md)
        self.plugin = plugin

    def run(self, root):
        default_style = self.plugin.config["default-style"]
        section_styles = self.plugin.config["section-styles"]
        style = default_style
        for element in root:
            if re.fullmatch(r"h[1-6]", element.tag):
                style = section_styles.get(element.get("id"), default_style)
            elif element.tag == "ul":
                self._process_list(element, style)

    def _process_list(self, ul, style):
        found = False
        for li in ul:
            if li.tag == "li" and self._process_entry(li):
                found = True
        if found:
            _add_class(ul, "awesome-list")
            _add_class(ul, f"awesome-list--{style}")

    def _process_entry(self, li):
        """Turn `<a>Name</a> - Description` into the card markup."""
        link = _entry_link(li)
        preview = None if link is None else self.plugin.previews.get(link.get("href"))
        if preview is None:
            return False
        url = link.get("href")

        _unwrap_paragraph(li)
        _wrap_description(li, "awesome-entry__desc")
        for child in li:
            if child.tag in ("ul", "ol"):
                self._process_sub_entries(child)
        li.remove(link)

        icon = self._icon(url, link)
        favicon = self._favicon_src(url)
        if favicon:
            img = etree.Element(
                "img",
                {"class": "awesome-entry__favicon", "src": favicon, "alt": "", "loading": "lazy"},
            )
            img.tail = link.text
            link.text = None
            link.insert(0, img)

        header = etree.Element("span", {"class": "awesome-entry__header"})
        _add_class(link, "awesome-entry__title")
        header.append(link)
        domain = etree.SubElement(header, "span", {"class": "awesome-entry__domain"})
        domain.text = _domain_label(url)

        li.text = None
        li.set("class", "awesome-entry")
        li.set("data-image", preview.image_kind)
        new_children = [icon, header]
        if preview.image:
            new_children.insert(0, self._media(url, preview))
        for i, child in enumerate(new_children):
            li.insert(i, child)
        return True

    def _media(self, url, preview):
        media = etree.Element(
            "a",
            {"class": "awesome-entry__media", "href": url, "tabindex": "-1", "aria-hidden": "true"},
        )
        etree.SubElement(media, "img", {"src": preview.image, "alt": "", "loading": "lazy"})
        return media

    def _favicon_src(self, url):
        host = _host(url)
        if not self.plugin.favicons.get(host):
            return None
        path = f"{ASSETS_DIR}/favicons/{_favicon_filename(host)}"
        return get_relative_url(path, self.plugin.page_url)

    def _icon(self, url, link):
        icon = etree.Element("span", {"class": "awesome-entry__icon", "aria-hidden": "true"})
        favicon = self._favicon_src(url)
        if favicon:
            etree.SubElement(icon, "img", {"src": favicon, "alt": "", "loading": "lazy"})
        else:
            icon.text = _plain_text(link)[:1].upper()
        return icon

    def _process_sub_entries(self, sub_list):
        _add_class(sub_list, "awesome-entry__subs")
        for li in sub_list:
            _add_class(li, "awesome-entry__sub")
            link = _entry_link(li)
            if link is None:
                continue
            _unwrap_paragraph(li)
            desc = _wrap_description(li, "awesome-entry__sub-desc")
            if _plain_text(desc):
                link.set("title", _plain_text(desc))


class AwesomeListExtension(Extension):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def extendMarkdown(self, md):
        # After "toc" (5) so headings have ids, and after MkDocs' "relpath" (0), which would
        # warn about the favicon paths as they aren't documentation files
        md.treeprocessors.register(_EntryTreeprocessor(md, self.plugin), "awesome_list", -1)


class AwesomeList:

    def __init__(self):
        self.config = {}
        self.previews = {}
        self.favicons = {}
        self.page_url = ""

    def on_config(self, config):
        # Hooks take no options of their own, so they live under `extra:` in mkdocs.yml
        self.config = LegacyConfig(CONFIG_SCHEME)
        self.config.load_dict(config.extra.get("awesome_list") or {})
        errors, warnings = self.config.validate()
        for key, message in warnings:
            log.warning("extra.awesome_list.%s: %s", key, message)
        if errors:
            raise ConfigurationError(
                "; ".join(f"extra.awesome_list.{key}: {message}" for key, message in errors)
            )

        config.markdown_extensions.append(AwesomeListExtension(self))
        # First, so the theme's and the user's CSS can override it
        config.extra_css.insert(0, f"{ASSETS_DIR}/{CSS_FILE}")
        return config

    def on_page_markdown(self, markdown, page=None, **kwargs):
        self.page_url = page.url if page else ""
        urls = {m.group(2) for m in ENTRY_RE.finditer(markdown)}.difference(self.previews)
        hosts = {_host(url) for url in urls}.difference(self.favicons)
        if not urls:
            return markdown

        print(f"\n[AwesomeList] Fetching {len(urls)} previews...", end=" ")
        sys.stdout.flush()
        urls, hosts = sorted(urls), sorted(hosts)
        with ThreadPoolExecutor(max_workers=10) as executor:
            previews = executor.map(_fetch_preview, urls)
            favicons = executor.map(_fetch_favicon, hosts)
            self.previews.update(zip(urls, previews))
            self.favicons.update(zip(hosts, favicons))
        print()

        if self.config["debug-log"]:
            for url in urls:
                preview = self.previews[url]
                print(f"  {url}\n    Image: {preview.image} ({preview.image_kind})")
        return markdown

    def on_post_build(self, config):
        assets_dir = os.path.join(config.site_dir, *ASSETS_DIR.split("/"))
        favicons_dir = os.path.join(assets_dir, "favicons")
        os.makedirs(favicons_dir, exist_ok=True)
        css_src = os.path.join(os.path.dirname(__file__), CSS_FILE)
        shutil.copyfile(css_src, os.path.join(assets_dir, CSS_FILE))
        for host, data in self.favicons.items():
            if data:
                with open(os.path.join(favicons_dir, _favicon_filename(host)), "wb") as f:
                    f.write(data)


# MkDocs calls a hook's module functions, so they share one instance
_awesome_list = AwesomeList()
on_config = _awesome_list.on_config
on_page_markdown = _awesome_list.on_page_markdown
on_post_build = _awesome_list.on_post_build
