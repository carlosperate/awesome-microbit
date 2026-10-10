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
import threading
import xml.etree.ElementTree as etree
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs.config import config_options
from mkdocs.config.base import LegacyConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.utils import get_relative_url
from PIL import Image, ImageOps
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import InvalidHeader, MaxRetryError, ResponseError
from urllib3.exceptions import TimeoutError as Urllib3Timeout
from webpreview import web_preview

log = logging.getLogger("mkdocs.hooks.awesome_list")

CONFIG_SCHEME = (
    ("debug-log", config_options.Type(bool, default=False)),
    ("default-style", config_options.Type(str, default="media")),
    ("section-styles", config_options.Type(dict, default={})),
    ("images", config_options.DictOfItems(config_options.File(exists=True), default={})),
)

# Styles without a preview image: index shows the favicon, and shelf only the `images` covers
NO_PREVIEW_STYLES = {"index", "shelf"}
ASSETS_DIR = "assets/awesome-list"
THUMBNAILS_DIR = f"{ASSETS_DIR}/thumbnails"
IMAGES_DIR = f"{ASSETS_DIR}/images"
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
# Requests at once to one site, as bursts from the build's ten threads get rate limited (429)
SITE_MAX_REQUESTS = 3
# The longest Retry-After worth waiting for: GitHub's preview images allow 100 an IP every 15
# minutes, and ask for 900s
RETRY_AFTER_MAX = 15 * 60
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


class _Retry(Retry):
    def parse_retry_after(self, retry_after):
        # A malformed one counts as none, rather than fail the request
        try:
            return super().parse_retry_after(retry_after)
        except InvalidHeader:
            return None

    def increment(self, method=None, url=None, response=None, error=None, _pool=None, **kwargs):
        seconds = (response is not None and self.get_retry_after(response)) or 0
        if seconds > RETRY_AFTER_MAX:
            # Returns the answer at once (raise_on_status is off), rather than retry into it early
            reason = ResponseError(f"{response.status} with a long Retry-After")
            raise MaxRetryError(_pool, url, reason)
        if seconds >= 60:
            # So the build doesn't look stuck
            print(f"\n[AwesomeList] {_pool.host} rate limited, waiting {seconds:.0f}s...", flush=True)
        return super().increment(method, url, response, error, _pool, **kwargs)


def _session():
    # Retries after 0s, 4s and 8s, or as long as Retry-After asks; a timed out read only once
    retry = _Retry(
        total=3,
        read=1,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


SESSION = _session()
SITE_SLOTS = {}
# What the current preview's requests were retried for, as urllib3 retries them out of sight
_retries = threading.local()


def _site(url):
    """The host's last two labels, or three for names like example.co.uk: what rate limits go by."""
    labels = (urlparse(url).hostname or "").split(".")
    count = 3 if len(labels) > 2 and len(labels[-1]) == 2 and len(labels[-2]) <= 3 else 2
    return ".".join(labels[-count:])


def _note_retries(resp):
    """Record what urllib3 retried the request for."""
    reasons = getattr(_retries, "reasons", None)
    if reasons is None:
        return
    for attempt in getattr(resp.raw.retries, "history", None) or ():
        timeout = isinstance(attempt.error, Urllib3Timeout)
        reasons.append(str(attempt.status or ("timeout" if timeout else "connection error")))


def _get(url, **kwargs):
    """GET the URL, switching user agent while the site blocks it."""
    # Held through the retries' waits too, so a rate-limited site gets fewer requests
    with SITE_SLOTS.setdefault(_site(url), threading.Semaphore(SITE_MAX_REQUESTS)):
        for user_agent in USER_AGENTS:
            resp = SESSION.get(url, timeout=10, headers={"User-Agent": user_agent}, **kwargs)
            _note_retries(resp)
            if resp.status_code not in BLOCKED_STATUSES or user_agent == USER_AGENTS[-1]:
                return resp
            resp.close()


def _failure(what, error):
    """The summary's heading for a request that raised, like "Image timed out"."""
    # requests wraps what urllib3 gave up on after its retries
    if error.args and isinstance(error.args[0], MaxRetryError):
        error = error.args[0].reason
    if isinstance(error, (requests.Timeout, Urllib3Timeout)):
        return f"{what} timed out"
    return f"{what} failed ({type(error).__name__})"


def _known_image_urls(url):
    """Preview images that follow from the link, best first: YouTube leaves its own out of the
    page it sends servers like the CI's, and GitHub's saves a request to a site that rate limits."""
    parsed = urlparse(url)
    host = _host(url)
    path = [part for part in parsed.path.split("/") if part]
    video = None
    if host in ("youtube.com", "m.youtube.com"):
        if path == ["watch"]:
            video = parse_qs(parsed.query).get("v", [None])[0]
        elif len(path) == 2 and path[0] in ("shorts", "embed", "live"):
            video = path[1]
    elif host == "youtu.be" and len(path) == 1:
        video = path[0]
    if video:
        # Only HD videos have the first, which the page shares when it exists
        names = ("maxresdefault", "hqdefault")
        return [f"https://i.ytimg.com/vi/{video}/{name}.jpg" for name in names]
    if host == "github.com" and len(path) >= 2:
        # The page's has a hash for the 1, which only busts GitHub's cache (or, rarely, the repo's
        # own picture, lost here)
        return [f"https://opengraph.githubassets.com/1/{path[0]}/{path[1]}"]
    return []


@dataclass
class Preview:
    image: Optional[str] = None
    # "picture", "logo" or "none"; tells the theme how to frame the image
    image_kind: str = "none"
    # The copy the site serves; without one the page links the original
    data: Optional[bytes] = field(default=None, repr=False, compare=False)
    # Where the site serves `data`, from the site's root
    path: Optional[str] = field(default=None, compare=False)
    # Width and height, for the images from the `images` option
    size: Optional[tuple] = field(default=None, compare=False)
    # Why there's no image, which the build's summary groups the entries by
    problem: Optional[str] = field(default=None, compare=False)
    # What its requests were retried for, as in _note_retries
    retries: tuple = field(default=(), compare=False)


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


def _image_src(preview, page_url):
    """The site's copy of the image, relative to the page, or else the original."""
    return get_relative_url(preview.path, page_url) if preview.path else preview.image


def _image_filename(image_url):
    return hashlib.sha1(image_url.encode()).hexdigest()[:16] + ".webp"


def _shrink_image(data):
    """Return the image's size, and the image as WebP shrunk to fit IMAGE_MAX_SIZE."""
    with Image.open(io.BytesIO(data)) as img:
        # Browsers rotate photos by their EXIF orientation, which a re-encoded copy loses
        ImageOps.exif_transpose(img, in_place=True)
        size = img.size
        mode = "RGBA" if img.has_transparency_data else "RGB"
        # convert() copies the full-size image even when it's already in that mode
        if img.mode != mode:
            img = img.convert(mode)
        img.thumbnail(IMAGE_MAX_SIZE)
        out = io.BytesIO()
        # Logos are already small enough, so they keep every pixel
        img.save(out, "WEBP", quality=80, lossless=_image_kind(*size) == "logo")
    return size, out.getvalue()


def _fetch_image(image_url):
    """Download an image and work out how to frame it."""
    try:
        with _get(image_url, stream=True) as resp:
            if resp.status_code >= 400:
                return Preview(problem=f"Image returned {resp.status_code}")
            content_type = resp.headers.get("Content-Type", "")
            data = resp.raw.read(IMAGE_MAX_BYTES + 1, decode_content=True)
    except Exception as e:
        return Preview(problem=_failure("Image", e))
    if not data:
        return Preview(problem="Empty image")
    if len(data) > IMAGE_MAX_BYTES:
        return Preview(problem=f"Image over {IMAGE_MAX_BYTES // 2**20}MB")
    if "svg" in content_type:
        # Browsers won't render a broken SVG, and some sites serve one
        if not data.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<"):
            return Preview(problem="Invalid SVG image")
        return Preview(image_url, "logo")
    try:
        size, webp = _shrink_image(data)
    except Exception:
        # Pillow can't read every format a browser can
        if content_type.startswith("image/"):
            return Preview(image_url, "picture")
        return Preview(problem="Image link isn't an image")
    path = f"{THUMBNAILS_DIR}/{_image_filename(image_url)}"
    return Preview(image_url, _image_kind(*size), webp, path)


def _fetch_preview(url):
    """Fetch the OpenGraph image of a page and work out how to frame it."""
    _retries.reasons = []
    preview = _find_preview(url)
    preview.retries = tuple(_retries.reasons)
    # A dot each, as fetching them all takes minutes
    print(".", end="", flush=True)
    return preview


def _find_preview(url):
    known = _known_image_urls(url)
    if known:
        # The page would only point at the same images, so it isn't worth a request
        for image in known:
            preview = _fetch_image(image)
            if preview.image:
                return preview
        return preview
    try:
        resp = _get(url)
    except Exception as e:
        return Preview(problem=_failure("Page", e))
    if not resp.ok:
        return Preview(problem=f"Page returned {resp.status_code}")
    # web_preview downloads an empty page again itself, with no timeout
    if not resp.content:
        return Preview(problem="Empty page")
    try:
        _title, _description, image = web_preview(url, content=resp.text)
        image = _resolve_image_url(image, url)
    except Exception as e:
        return Preview(problem=f"Couldn't read the page ({type(e).__name__})")
    return _fetch_image(image) if image else Preview(problem="No preview image on the page")


def _local_image(path):
    """Load an image from the `images` option, which the site serves as it is."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        with Image.open(io.BytesIO(data)) as img:
            size = img.size
    except OSError as e:
        raise ConfigurationError(f"extra.awesome_list.images: can't read {path} ({e})")
    site_path = f"{IMAGES_DIR}/{os.path.basename(path)}"
    return Preview(path, _image_kind(*size), data, site_path, size)


def _fetch_favicon(host):
    """Return the site's favicon as PNG bytes, or None."""
    try:
        # Not _get: every favicon comes from Google's service, which doesn't need limiting
        resp = SESSION.get(FAVICON_URL.format(host=host), timeout=10)
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
    """The web link an item starts with, unless it's an image link (a badge), or None."""
    container = li
    # Loose lists (blank lines between items) wrap each item's text in a <p>
    if len(li) and li[0].tag == "p" and not (li.text or "").strip():
        container = li[0]
    if (container.text or "").strip() or not len(container):
        return None
    link = container[0]
    if link.tag != "a" or (not (link.text or "").strip() and len(link) and link[0].tag == "img"):
        return None
    return link if re.match(r"https?://", link.get("href", "")) else None


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


def _move_sub_entries(ul, li, sub_lists, name):
    """Move an entry's sub-entries to an item of their own after it, for smaller cards under its."""
    row = etree.Element("li", {"class": "awesome-subs"})
    for sub_list in sub_lists:
        li.remove(sub_list)
        sub_list.tail = None
        # Out of the entry, so the list says whose they are
        sub_list.set("aria-label", f"Related to {name}")
        row.append(sub_list)
    ul.insert(list(ul).index(li) + 1, row)


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
        lists = []
        for element in root:
            if re.fullmatch(r"h[1-6]", element.tag):
                style = section_styles.get(element.get("id"), default_style)
            elif element.tag == "ul":
                lists.append((element, style))
        # Fetched here, where each list's style says what its entries show
        entries = []
        for ul, style in lists:
            links = (_entry_link(li) for li in ul)
            entries += [(a.get("href"), _plain_text(a), style) for a in links if a is not None]
        self.plugin.fetch(entries)
        for ul, style in lists:
            self._process_list(ul, style)

    def _process_list(self, ul, style):
        found = False
        for li in list(ul):
            if li.tag == "li" and self._process_entry(ul, li, style):
                found = True
        if found:
            _add_class(ul, "awesome-list")
            # Gallery cards are media cards in columns, so they get the media rules too
            if style == "gallery":
                _add_class(ul, "awesome-list--media")
            _add_class(ul, f"awesome-list--{style}")

    def _process_entry(self, ul, li, style):
        """Turn `<a>Name</a> - Description` into the card markup."""
        link = _entry_link(li)
        if link is None:
            return False
        preview = self._preview(link, style)
        url = link.get("href")

        _unwrap_paragraph(li)
        _wrap_description(li, "awesome-entry__desc")
        sub_lists = [child for child in li if child.tag in ("ul", "ol")]
        as_cards = style == "media"
        for sub_list in sub_lists:
            self._process_sub_entries(sub_list, as_cards)
        li.remove(link)

        icon = self._icon(url, link)
        self._add_favicon(link)

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
        elif as_cards and sub_lists:
            _move_sub_entries(ul, li, sub_lists, _plain_text(link))
        return True

    def _preview(self, link, style):
        """The entry's preview, an empty one for styles that don't show it."""
        url = link.get("href")
        if style == "shelf" and url not in self.plugin.config["images"]:
            # A page's preview isn't always the cover, so shelves only show the given images
            name = _plain_text(link)
            log.warning('No cover in extra.awesome_list.images for "%s": %s', name, url)
            return Preview()
        return self.plugin.previews.get(url, Preview())

    def _media(self, url, preview):
        media = etree.Element(
            "a",
            {"class": "awesome-entry__media", "href": url, "tabindex": "-1", "aria-hidden": "true"},
        )
        src = _image_src(preview, self.plugin.page_url)
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

    def _add_favicon(self, link):
        favicon = self._favicon_src(link.get("href"))
        if favicon:
            img = etree.Element(
                "img",
                {"class": "awesome-entry__favicon", "src": favicon, "alt": "", "loading": "lazy"},
            )
            img.tail = link.text
            link.text = None
            link.insert(0, img)

    def _icon(self, url, link):
        icon = etree.Element("span", {"class": "awesome-entry__icon", "aria-hidden": "true"})
        favicon = self._favicon_src(url)
        if favicon:
            etree.SubElement(icon, "img", {"src": favicon, "alt": "", "loading": "lazy"})
        else:
            icon.text = _plain_text(link)[:1].upper()
        return icon

    def _process_sub_entries(self, sub_list, as_cards):
        _add_class(sub_list, "awesome-entry__subs")
        for li in sub_list:
            _add_class(li, "awesome-entry__sub")
            link = _entry_link(li)
            if link is None:
                continue
            _unwrap_paragraph(li)
            desc = _wrap_description(li, "awesome-entry__sub-desc")
            if as_cards:
                # Their cards show the description, and the favicon if the build has it for an entry
                self._add_favicon(link)
            elif _plain_text(desc):
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
        # By URL, with the `images` option's images in place of their pages' previews
        self.previews = {}
        self.favicons = {}
        # Entry names by URL, in list order, for the thumbnails page
        self.names = {}
        self.page_url = ""

    def on_config(self, config):
        # Hooks take no options of their own, so they live under `extra:` in mkdocs.yml
        # The config file's path resolves the `images` option's files next to it
        self.config = LegacyConfig(CONFIG_SCHEME, config_file_path=config.config_file_path)
        self.config.load_dict(config.extra.get("awesome_list") or {})
        errors, warnings = self.config.validate()
        for key, message in warnings:
            log.warning("extra.awesome_list.%s: %s", key, message)
        if errors:
            raise ConfigurationError(
                "; ".join(f"extra.awesome_list.{key}: {message}" for key, message in errors)
            )

        # The site serves them from one folder, by file name
        names = [os.path.basename(path) for path in self.config["images"].values()]
        if len(set(names)) < len(names):
            raise ConfigurationError("extra.awesome_list.images: two files have the same name")
        self.previews.update(
            (url, _local_image(path)) for url, path in self.config["images"].items()
        )

        config.markdown_extensions.append(AwesomeListExtension(self))
        # First, so the theme's and the user's CSS can override it
        config.extra_css.insert(0, f"{ASSETS_DIR}/{CSS_FILE}")
        return config

    def on_page_markdown(self, markdown, page=None, **kwargs):
        # For the treeprocessor's relative links
        self.page_url = page.url if page else ""
        return markdown

    def fetch(self, entries):
        """Fetch the previews of the (url, name, style) entries whose style shows one, and every
        entry's favicon, skipping what's already fetched."""
        for url, name, _ in entries:
            self.names.setdefault(url, name)
        urls = {url for url, _, style in entries if style not in NO_PREVIEW_STYLES}
        urls.difference_update(self.previews)
        hosts = {_host(url) for url, _, _ in entries}.difference(self.favicons)
        if not urls and not hosts:
            return

        print(f"\n[AwesomeList] Fetching {len(urls)} previews...", end=" ", flush=True)
        urls, hosts = sorted(urls), sorted(hosts)
        with ThreadPoolExecutor(max_workers=10) as executor:
            previews = executor.map(_fetch_preview, urls)
            favicons = executor.map(_fetch_favicon, hosts)
            self.previews.update(zip(urls, previews))
            self.favicons.update(zip(hosts, favicons))
        print()
        print(self._summary(urls, hosts))

        if self.config["debug-log"]:
            for url in urls:
                preview = self.previews[url]
                print(f"  {url}\n    Image: {preview.image} ({preview.image_kind})")

    def _summary(self, urls, hosts):
        """What the fetching found, with the entries without an image by why, and the retried ones."""
        kinds = [self.previews[url].image_kind for url in urls]
        favicons = sum(1 for host in hosts if self.favicons[host])
        lines = [
            f"[AwesomeList] {len(urls)} previews: {kinds.count('picture')} pictures, "
            f"{kinds.count('logo')} logos, {kinds.count('none')} without an image. "
            f"Favicons for {favicons} of {len(hosts)} sites."
        ]
        groups, retried = {}, []
        for url in urls:
            preview = self.previews[url]
            if preview.image_kind == "none":
                groups.setdefault(preview.problem or "No image", []).append(url)
            elif preview.retries:
                retried.append(url)
        # The biggest groups first, and the ones that worked out last
        order = sorted(groups, key=lambda h: (-len(groups[h]), h))
        sections = [(heading, groups[heading], "") for heading in order]
        if retried:
            past = Counter(r for url in retried for r in self.previews[url].retries)
            tally = ", ".join(f"{r} x{n}" for r, n in past.most_common())
            sections.append(("Found after retrying", retried, f", past {tally}"))
        for heading, group, extra in sections:
            lines.append(f"  {heading} ({len(group)}){extra}:")
            for url in group:
                retries = self.previews[url].retries
                lines.append(f"    {url}" + (f" (after {', '.join(retries)})" if retries else ""))
        return "\n".join(lines)

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
        for preview in self.previews.values():
            if preview.path:
                dest = os.path.join(config.site_dir, *preview.path.split("/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as f:
                    f.write(preview.data)
        thumbnails_dir = os.path.join(config.site_dir, *THUMBNAILS_DIR.split("/"))
        os.makedirs(thumbnails_dir, exist_ok=True)
        with open(os.path.join(thumbnails_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(self._thumbnails_page())
        for url in self.config["images"].keys() - self.names.keys():
            log.warning("extra.awesome_list.images: no entry links to %s", url)

    def _thumbnails_page(self):
        items = []
        for url, name in self.names.items():
            preview = self.previews.get(url)
            if not preview or not preview.image:
                continue
            src = _image_src(preview, f"{THUMBNAILS_DIR}/index.html")
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
