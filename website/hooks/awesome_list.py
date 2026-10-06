"""
Turns each awesome-list entry into a card with the linked page's preview image and favicon.
The options and the markup the theme styles are in hooks/README.md.
"""

import hashlib
import html
import io
import logging
import os
import re
import shutil
import sys
import xml.etree.ElementTree as etree
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs.config import config_options
from mkdocs.config.base import LegacyConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.utils import get_relative_url
from PIL import Image, ImageOps
from requests.adapters import HTTPAdapter, Retry
from webpreview import web_preview

log = logging.getLogger("mkdocs.hooks.awesome_list")

CONFIG_SCHEME = (
    ("debug-log", config_options.Type(bool, default=False)),
    ("default-style", config_options.Type(str, default="media")),
    ("section-styles", config_options.Type(dict, default={})),
    ("images", config_options.Type(dict, default={})),
)

# A top-level item starting with a web link; image links (badges) and in-page links aren't entries
ENTRY_RE = re.compile(r"^- \[(?!!)(.*?)\]\(\s*(https?://[^)\s]+)\s*\)", re.MULTILINE)
ASSETS_DIR = "assets/awesome-list"
THUMBNAILS_DIR = f"{ASSETS_DIR}/thumbnails"
IMAGES_DIR = f"{ASSETS_DIR}/books"
CSS_FILE = "awesome-list.css"
FAVICON_URL = "https://www.google.com/s2/favicons?domain={host}&sz=64"
# Tried in turn while a site answers as if it blocks the client. Python's default goes first, as
# some sites (YouTube, Springer) serve the other a page without the preview tags.
USER_AGENTS = (
    requests.utils.default_user_agent(),
    "Mozilla/5.0 (compatible; mkdocs-awesomelist)",
)
# 999 is LinkedIn's answer to bots
BLOCKED_STATUSES = (403, 405, 406, 999)
# Three times the media frame in awesome-list.css (200px wide, 1.91:1): 3x screens, or 2x zoomed in
IMAGE_MAX_SIZE = (600, 315)
# The biggest preview in the list was 14MB
IMAGE_MAX_BYTES = 25 * 1024 * 1024
CODE_HOSTS = ("github.com", "gitlab.com")

# Every card image, smaller than on the cards, to check them by eye; nothing on the site links to it
THUMBNAILS_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<title>Card images</title>
<style>
body {{ margin: 16px; font: 13px/1.4 system-ui, sans-serif; color: #222; background: #fff; }}
ol {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px 12px;
    margin: 0;
    padding: 0;
    list-style: none;
}}
img {{ display: block; width: 100%; aspect-ratio: 1.91; object-fit: contain; background: #eee; }}
a {{ color: inherit; overflow-wrap: anywhere; }}
</style>
</head>
<body>
<h1>{count} card images</h1>
<ol>
{items}
</ol>
</body>
</html>
"""
THUMBNAIL_ITEM = (
    '<li><a href="{src}"><img src="{src}" alt="" loading="lazy"></a><a href="{url}">{name}</a></li>'
)


def _session():
    # Retries after 0s, 2s and 4s; slow sites stay slow, so a timed out read only once
    retry = Retry(
        total=3,
        read=1,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        # A long Retry-After would hold up the build
        respect_retry_after_header=False,
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


SESSION = _session()


def _get(url, **kwargs):
    """GET the URL, switching user agent while the site blocks it."""
    for user_agent in USER_AGENTS[:-1]:
        resp = SESSION.get(url, timeout=10, headers={"User-Agent": user_agent}, **kwargs)
        if resp.status_code not in BLOCKED_STATUSES:
            return resp
        resp.close()
    return SESSION.get(url, timeout=10, headers={"User-Agent": USER_AGENTS[-1]}, **kwargs)


@dataclass
class Preview:
    image: Optional[str] = None
    # "picture", "logo" or "none"; tells the theme how to frame the image
    image_kind: str = "none"
    # The shrunk WebP copy the site serves; without one the page links the original
    data: Optional[bytes] = field(default=None, repr=False, compare=False)
    # Width and height, for the images from the `images` option
    size: Optional[tuple] = field(default=None, compare=False)


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


def _image_filename(image_url):
    return hashlib.sha1(image_url.encode()).hexdigest()[:16] + ".webp"


def _download_image(image_url):
    """Return the image's bytes and content type, or None if it can't be loaded."""
    try:
        with _get(image_url, stream=True) as resp:
            if resp.status_code >= 400:
                print(f"\n  WARNING: Image returned {resp.status_code}: {image_url}")
                return None
            content_type = resp.headers.get("Content-Type", "")
            data = resp.raw.read(IMAGE_MAX_BYTES + 1, decode_content=True)
    except Exception as e:
        print(f"\n  WARNING: Could not reach image: {image_url} ({e})")
        return None
    if not data:
        print(f"\n  WARNING: Empty image: {image_url}")
        return None
    if len(data) > IMAGE_MAX_BYTES:
        print(f"\n  WARNING: Image over {IMAGE_MAX_BYTES // 2**20}MB: {image_url}")
        return None
    return data, content_type


def _shrink_image(data):
    """Return the image's size, and the image as WebP shrunk to fit IMAGE_MAX_SIZE."""
    with Image.open(io.BytesIO(data)) as img:
        # Browsers rotate photos by their EXIF orientation, which a re-encoded copy loses
        img = ImageOps.exif_transpose(img)
    size = img.size
    img = img.convert("RGBA" if img.has_transparency_data else "RGB")
    img.thumbnail(IMAGE_MAX_SIZE)
    out = io.BytesIO()
    # Logos are already small enough, so they keep every pixel
    img.save(out, "WEBP", quality=80, lossless=_image_kind(*size) == "logo")
    return size, out.getvalue()


def _fetch_image(image_url):
    """Download an image and work out how to frame it."""
    downloaded = _download_image(image_url)
    if not downloaded:
        return Preview()
    data, content_type = downloaded
    if "svg" in content_type:
        # Browsers won't render a broken SVG, and some sites serve one
        if not data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
            print(f"\n  WARNING: Invalid SVG image: {image_url}")
            return Preview()
        return Preview(image_url, "logo")
    try:
        size, webp = _shrink_image(data)
    except Exception:
        # Pillow can't read every format a browser can
        return Preview(image_url, "picture") if content_type.startswith("image/") else Preview()
    return Preview(image_url, _image_kind(*size), webp)


def _fetch_preview(url):
    """Fetch the OpenGraph image of a page and work out how to frame it."""
    try:
        resp = _get(url)
        resp.raise_for_status()
        _title, _description, image = web_preview(url, content=resp.text)
        image = _resolve_image_url(image, url)
    except Exception as e:
        print(f"\n[AwesomeList] Error fetching preview for {url}: {e}")
        return Preview()
    return _fetch_image(image) if image else Preview()


def _local_image(path, root):
    """Load an image from the `images` option, which the site serves as it is."""
    try:
        with open(os.path.join(root, path), "rb") as f:
            data = f.read()
        with Image.open(io.BytesIO(data)) as img:
            size = img.size
    except OSError as e:
        raise ConfigurationError(f"extra.awesome_list.images: can't read {path} ({e})")
    return Preview(path, _image_kind(*size), data, size)


def _local_image_path(path):
    """Where the site serves an image from the `images` option."""
    return f"{IMAGES_DIR}/{os.path.basename(path)}"


def _fetch_favicon(host):
    """Return the site's favicon as PNG bytes, or None."""
    try:
        resp = _get(FAVICON_URL.format(host=host))
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


def _wrap_details(li, header):
    """Move the header and what follows into one element, which shelves show over the cover."""
    details = etree.Element("div", {"class": "awesome-entry__details"})
    children = list(li)
    for child in children[children.index(header):]:
        li.remove(child)
        details.append(child)
    li.append(details)


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
            if li.tag == "li" and self._process_entry(li, style):
                found = True
        if found:
            _add_class(ul, "awesome-list")
            _add_class(ul, f"awesome-list--{style}")

    def _process_entry(self, li, style):
        """Turn `<a>Name</a> - Description` into the card markup."""
        link = _entry_link(li)
        preview = None if link is None else self._preview(link, style)
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
        if style == "shelf":
            _wrap_details(li, header)
        return True

    def _preview(self, link, style):
        """The entry's image from the `images` option, or its page's preview, or None if neither."""
        url = link.get("href")
        image = self.plugin.images.get(url)
        if image or url not in self.plugin.previews:
            return image
        if style == "shelf":
            # A page's preview isn't always the cover, so shelves only show the given images
            name = _plain_text(link)
            log.warning('No cover in extra.awesome_list.images for "%s": %s', name, url)
            return Preview()
        return self.plugin.previews[url]

    def _media(self, url, preview):
        media = etree.Element(
            "a",
            {"class": "awesome-entry__media", "href": url, "tabindex": "-1", "aria-hidden": "true"},
        )
        src = preview.image
        if url in self.plugin.images:
            src = get_relative_url(_local_image_path(preview.image), self.plugin.page_url)
        elif preview.data is not None:
            path = f"{THUMBNAILS_DIR}/{_image_filename(preview.image)}"
            src = get_relative_url(path, self.plugin.page_url)
        img = etree.SubElement(media, "img", {"src": src, "alt": "", "loading": "lazy"})
        if preview.size:
            # So the browser can lay it out before it loads
            img.set("width", str(preview.size[0]))
            img.set("height", str(preview.size[1]))
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
        # The `images` option's images, by URL
        self.images = {}
        self.favicons = {}
        # Entry names by URL, in list order, for the thumbnails page
        self.names = {}
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

        root = os.path.dirname(config.config_file_path)
        self.images = {url: _local_image(path, root) for url, path in self.config["images"].items()}
        # The site serves them from one folder, by file name
        names = [os.path.basename(path) for path in self.config["images"].values()]
        if len(set(names)) < len(names):
            raise ConfigurationError("extra.awesome_list.images: two files have the same name")

        config.markdown_extensions.append(AwesomeListExtension(self))
        # First, so the theme's and the user's CSS can override it
        config.extra_css.insert(0, f"{ASSETS_DIR}/{CSS_FILE}")
        return config

    def on_page_markdown(self, markdown, page=None, **kwargs):
        self.page_url = page.url if page else ""
        for m in ENTRY_RE.finditer(markdown):
            self.names.setdefault(m.group(2), m.group(1))
        urls = set(self.names).difference(self.previews, self.images)
        hosts = {_host(url) for url in self.names}.difference(self.favicons)
        if not urls and not hosts:
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
        thumbnails_dir = os.path.join(config.site_dir, *THUMBNAILS_DIR.split("/"))
        os.makedirs(thumbnails_dir, exist_ok=True)
        for preview in self.previews.values():
            if preview.data is not None:
                with open(os.path.join(thumbnails_dir, _image_filename(preview.image)), "wb") as f:
                    f.write(preview.data)
        images_dir = os.path.join(config.site_dir, *IMAGES_DIR.split("/"))
        os.makedirs(images_dir, exist_ok=True)
        for preview in self.images.values():
            with open(os.path.join(images_dir, os.path.basename(preview.image)), "wb") as f:
                f.write(preview.data)
        with open(os.path.join(thumbnails_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(self._thumbnails_page())
        for url in self.images.keys() - self.names.keys():
            log.warning("extra.awesome_list.images: no entry links to %s", url)

    def _thumbnails_page(self):
        items = []
        for url, name in self.names.items():
            preview = self.images.get(url) or self.previews.get(url)
            if not preview or not preview.image:
                continue
            if url in self.images:
                page = f"{THUMBNAILS_DIR}/index.html"
                src = get_relative_url(_local_image_path(preview.image), page)
            elif preview.data is None:
                src = preview.image
            else:
                src = _image_filename(preview.image)
            items.append(
                THUMBNAIL_ITEM.format(
                    src=html.escape(src), url=html.escape(url), name=html.escape(name)
                )
            )
        return THUMBNAILS_PAGE.format(count=len(items), items="\n".join(items))


# MkDocs calls a hook's module functions, so they share one instance
_awesome_list = AwesomeList()
on_config = _awesome_list.on_config
on_page_markdown = _awesome_list.on_page_markdown
on_post_build = _awesome_list.on_post_build
