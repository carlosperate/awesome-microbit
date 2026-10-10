"""Tests for the awesome_list MkDocs hook."""

import io
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import markdown
import pytest
import requests
from mkdocs.exceptions import ConfigurationError
from PIL import Image
from urllib3 import HTTPResponse
from urllib3.exceptions import MaxRetryError, ReadTimeoutError
from urllib3.util.retry import RequestHistory
from webpreview import web_preview

from awesome_list import (
    AwesomeList,
    AwesomeListExtension,
    RETRY_AFTER_MAX,
    SITE_MAX_REQUESTS,
    USER_AGENTS,
    Preview,
    _Retry,
    _domain_label,
    _failure,
    _fetch_image,
    _fetch_preview,
    _get,
    _image_filename,
    _image_kind,
    _known_image_urls,
    _local_image,
    _resolve_image_url,
    _site,
)


def _image_bytes(width, height, fmt="PNG", **save_options):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height)).save(buffer, fmt, **save_options)
    return buffer.getvalue()


def _webp_size(data):
    with Image.open(io.BytesIO(data)) as img:
        assert img.format == "WEBP"
        return img.size


def _image_response(status=200, content_type="image/png", body=b""):
    resp = MagicMock(status_code=status, headers={"Content-Type": content_type})
    resp.raw.read.return_value = body
    resp.__enter__.return_value = resp
    return resp


# An image from the `images` option
COVER = Preview(
    "images/a.webp", "picture", b"webp", "assets/awesome-list/images/a.webp", (300, 400)
)
# A preview shrunk by _fetch_image
THUMBNAIL = "assets/awesome-list/thumbnails/a.webp"
SHRUNK = Preview("https://a.example.com/og.png", "picture", b"og", THUMBNAIL)


def _make_plugin(default_style="media", section_styles=None, images=None):
    """A plugin as on_config leaves it, with `images` as the option's previews by URL."""
    plugin = AwesomeList()
    images = images or {}
    plugin.config = {
        "debug-log": False,
        "default-style": default_style,
        "section-styles": section_styles or {},
        "images": {url: preview.image for url, preview in images.items()},
    }
    plugin.previews.update(images)
    return plugin


def _render(plugin, text):
    return markdown.markdown(text, extensions=["toc", AwesomeListExtension(plugin)])


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------


class TestResolveImageUrl:

    @pytest.mark.parametrize("image", [None, ""])
    def test_no_image(self, image):
        assert _resolve_image_url(image, "https://example.com") is None

    def test_absolute_url_kept(self):
        url = "http://cdn.example.com/img.png"
        assert _resolve_image_url(url, "https://example.com") == url

    def test_protocol_relative(self):
        result = _resolve_image_url("//cdn.example.com/img.png", "https://example.com")
        assert result == "https://cdn.example.com/img.png"

    def test_absolute_path(self):
        result = _resolve_image_url("/assets/img.png", "https://example.com/page")
        assert result == "https://example.com/assets/img.png"

    def test_relative_path(self):
        result = _resolve_image_url("img.png", "https://example.com/page/")
        assert result == "https://example.com/page/img.png"


class TestImageKind:

    @pytest.mark.parametrize(
        "size, kind",
        [
            ((1200, 630), "picture"),
            ((2100, 1750), "picture"),
            ((600, 600), "picture"),
            ((153, 232), "picture"),
            ((180, 180), "logo"),
            ((64, 64), "logo"),
        ],
    )
    def test_kind(self, size, kind):
        assert _image_kind(*size) == kind


@patch("awesome_list.SESSION.get")
class TestGet:

    def test_next_user_agent_while_blocked(self, mock_get):
        mock_get.side_effect = [MagicMock(status_code=403), MagicMock(status_code=200)]
        assert _get("https://example.com").status_code == 200
        agents = [c.kwargs["headers"]["User-Agent"] for c in mock_get.call_args_list]
        assert agents == list(USER_AGENTS)

    def test_other_errors_keep_the_user_agent(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        assert _get("https://example.com").status_code == 404
        assert mock_get.call_count == 1

    def test_requests_to_one_site_at_once_are_limited(self, mock_get):
        running, most = 0, 0
        lock = threading.Lock()

        def get(*args, **kwargs):
            nonlocal running, most
            with lock:
                running += 1
                most = max(most, running)
            time.sleep(0.02)
            with lock:
                running -= 1
            return MagicMock(status_code=200)

        mock_get.side_effect = get
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(_get, [f"https://a{i}.limited.example" for i in range(10)]))
        assert most == SITE_MAX_REQUESTS


class TestRetry:

    def test_short_retry_after_is_retried(self, capsys):
        response = HTTPResponse(status=429, headers={"Retry-After": str(RETRY_AFTER_MAX)})
        pool = MagicMock(host="example.com")
        retry = _Retry(total=3, status_forcelist=(429,)).increment("GET", "/", response, _pool=pool)
        assert retry.total == 2
        assert retry.get_retry_after(response) == RETRY_AFTER_MAX
        assert f"example.com rate limited, waiting {RETRY_AFTER_MAX}s" in capsys.readouterr().out

    def test_malformed_retry_after_ignored(self):
        response = HTTPResponse(status=503, headers={"Retry-After": "soon"})
        retry = _Retry(total=3, status_forcelist=(503,)).increment("GET", "/", response)
        assert retry.get_retry_after(response) is None

    def test_long_retry_after_gives_up(self):
        response = HTTPResponse(status=429, headers={"Retry-After": str(RETRY_AFTER_MAX + 1)})
        with pytest.raises(MaxRetryError):
            _Retry(total=3, status_forcelist=(429,)).increment("GET", "/", response)


class TestFailure:

    def test_timeout_after_retries(self):
        error = requests.ConnectionError(MaxRetryError(None, "/", ReadTimeoutError(None, "/", "")))
        assert _failure("Page", error) == "Page timed out"

    def test_other_errors_named(self):
        assert _failure("Page", requests.ConnectionError("refused")) == "Page failed (ConnectionError)"


class TestSite:

    @pytest.mark.parametrize(
        "url, site",
        [
            ("https://github.com/owner/repo", "github.com"),
            ("https://opengraph.githubassets.com/1/owner/repo", "githubassets.com"),
            ("https://someone.blogspot.com/2017/post.html", "blogspot.com"),
            ("https://kitronik.co.uk/blogs/resources", "kitronik.co.uk"),
            ("https://core-electronics.com.au/guides/", "core-electronics.com.au"),
            ("https://cdn.hackaday.io/images/a.jpg", "hackaday.io"),
        ],
    )
    def test_site(self, url, site):
        assert _site(url) == site


class TestKnownImageUrls:

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/watch?v=abc123",
            "https://youtube.com/watch?v=abc123&t=42",
            "https://m.youtube.com/watch?v=abc123",
            "https://youtu.be/abc123",
            "https://www.youtube.com/shorts/abc123",
            "https://www.youtube.com/embed/abc123",
        ],
    )
    def test_youtube_video(self, url):
        assert _known_image_urls(url) == [
            "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
            "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
        ]

    @pytest.mark.parametrize(
        "url",
        ["https://github.com/owner/repo", "https://github.com/owner/repo/tree/main/docs#readme"],
    )
    def test_github_repository(self, url):
        assert _known_image_urls(url) == ["https://opengraph.githubassets.com/1/owner/repo"]

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/playlist?list=PL123",
            "https://www.youtube.com/@microbit_edu",
            "https://www.youtube.com/watch",
            "https://github.com/owner",
            "https://example.com/watch?v=abc123",
        ],
    )
    def test_others_need_their_page(self, url):
        assert _known_image_urls(url) == []


@patch("awesome_list.SESSION.get")
class TestFetchImage:

    @pytest.mark.parametrize(
        "size, shrunk",
        [((1200, 630), (600, 315)), ((600, 1200), (157, 315)), ((4000, 1000), (600, 150))],
    )
    def test_picture_shrunk_keeping_its_ratio(self, mock_get, size, shrunk):
        mock_get.return_value = _image_response(body=_image_bytes(*size))
        preview = _fetch_image("https://example.com/og.png")
        assert preview == Preview("https://example.com/og.png", "picture")
        assert _webp_size(preview.data) == shrunk
        thumbnail = _image_filename("https://example.com/og.png")
        assert preview.path == f"assets/awesome-list/thumbnails/{thumbnail}"

    def test_logo_keeps_its_size(self, mock_get):
        mock_get.return_value = _image_response(body=_image_bytes(180, 180))
        preview = _fetch_image("https://example.com/icon.png")
        assert preview == Preview("https://example.com/icon.png", "logo")
        assert _webp_size(preview.data) == (180, 180)

    def test_photo_rotated_by_its_exif_orientation(self, mock_get):
        exif = Image.Exif()
        exif[0x0112] = 6  # Orientation: rotate 90°
        body = _image_bytes(300, 600, "JPEG", exif=exif)
        mock_get.return_value = _image_response(content_type="image/jpeg", body=body)
        assert _webp_size(_fetch_image("https://example.com/photo.jpg").data) == (600, 300)

    def test_svg_is_linked(self, mock_get):
        body = b'\n<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>'
        mock_get.return_value = _image_response(content_type="image/svg+xml", body=body)
        preview = _fetch_image("https://example.com/logo.svg")
        assert preview == Preview("https://example.com/logo.svg", "logo")
        assert preview.data is None

    def test_broken_svg(self, mock_get):
        body = b'?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>'
        mock_get.return_value = _image_response(content_type="image/svg+xml", body=body)
        preview = _fetch_image("https://example.com/logo.svg")
        assert preview == Preview()
        assert preview.problem == "Invalid SVG image"

    def test_unreadable_image_format_is_linked(self, mock_get):
        mock_get.return_value = _image_response(content_type="image/jxl", body=b"...")
        preview = _fetch_image("https://example.com/img.jxl")
        assert preview == Preview("https://example.com/img.jxl", "picture")
        assert preview.data is None

    def test_http_error(self, mock_get):
        mock_get.return_value = _image_response(status=404)
        preview = _fetch_image("https://example.com/missing.png")
        assert preview == Preview()
        assert preview.problem == "Image returned 404"

    def test_network_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("refused")
        preview = _fetch_image("https://example.com/img.png")
        assert preview == Preview()
        assert preview.problem == "Image failed (ConnectionError)"

    def test_empty_image(self, mock_get):
        mock_get.return_value = _image_response(body=b"")
        preview = _fetch_image("https://example.com/og.png")
        assert preview == Preview()
        assert preview.problem == "Empty image"

    @patch("awesome_list.IMAGE_MAX_BYTES", 10)
    def test_image_too_big(self, mock_get):
        mock_get.return_value = _image_response(body=_image_bytes(1200, 630))
        assert _fetch_image("https://example.com/og.png") == Preview()

    def test_not_an_image(self, mock_get):
        mock_get.return_value = _image_response(content_type="text/html", body=b"<html>")
        preview = _fetch_image("https://example.com/page")
        assert preview == Preview()
        assert preview.problem == "Image link isn't an image"


@patch("awesome_list._fetch_image")
@patch("awesome_list.web_preview")
@patch("awesome_list.SESSION.get")
class TestFetchPreview:

    def test_image_found(self, mock_get, mock_preview, mock_image):
        mock_preview.return_value = ("Title", "Desc", "/og.png")
        mock_image.return_value = Preview("https://example.com/og.png", "picture")

        assert _fetch_preview("https://example.com/page") == mock_image.return_value
        mock_preview.assert_called_once_with(
            "https://example.com/page", content=mock_get.return_value.text
        )
        mock_image.assert_called_once_with("https://example.com/og.png")

    def test_no_image(self, mock_get, mock_preview, mock_image):
        mock_preview.return_value = ("Title", "Desc", None)
        preview = _fetch_preview("https://example.com")
        assert preview == Preview()
        assert preview.problem == "No preview image on the page"
        mock_image.assert_not_called()

    def test_malformed_image_url(self, mock_get, mock_preview, mock_image):
        mock_preview.return_value = ("Title", "Desc", "http://[broken")
        assert _fetch_preview("https://example.com") == Preview()
        mock_image.assert_not_called()

    def test_page_error(self, mock_get, mock_preview, mock_image):
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 404
        preview = _fetch_preview("https://example.com")
        assert preview == Preview()
        assert preview.problem == "Page returned 404"
        mock_preview.assert_not_called()

    def test_empty_page(self, mock_get, mock_preview, mock_image):
        mock_get.return_value.content = b""
        preview = _fetch_preview("https://example.com")
        assert preview == Preview()
        assert preview.problem == "Empty page"
        mock_preview.assert_not_called()

    def test_known_image_skips_the_page(self, mock_get, mock_preview, mock_image):
        mock_image.return_value = Preview("https://i.ytimg.com/vi/abc/maxresdefault.jpg", "picture")
        assert _fetch_preview("https://youtu.be/abc") == mock_image.return_value
        mock_image.assert_called_once_with("https://i.ytimg.com/vi/abc/maxresdefault.jpg")
        mock_get.assert_not_called()

    def test_next_known_image_when_one_is_missing(self, mock_get, mock_preview, mock_image):
        hq = Preview("https://i.ytimg.com/vi/abc/hqdefault.jpg", "picture")
        mock_image.side_effect = [Preview(), hq]
        assert _fetch_preview("https://youtu.be/abc") == hq
        mock_get.assert_not_called()

    def test_no_page_when_known_images_fail(self, mock_get, mock_preview, mock_image):
        mock_image.return_value = Preview(problem="Image returned 429")
        assert _fetch_preview("https://github.com/owner/repo").problem == "Image returned 429"
        mock_get.assert_not_called()

    def test_retries_recorded(self, mock_get, mock_preview, mock_image):
        mock_get.return_value.raw.retries.history = (
            RequestHistory("GET", "/", None, 429, None),
            RequestHistory("GET", "/", ReadTimeoutError(None, "/", ""), None, None),
        )
        mock_preview.return_value = ("Title", "Desc", "/og.png")
        mock_image.return_value = Preview("https://example.com/og.png", "picture")
        preview = _fetch_preview("https://example.com")
        assert preview.retries == ("429", "timeout")

    def test_retries_before_a_blocked_answer_recorded(self, mock_get, mock_preview, mock_image):
        blocked = MagicMock(status_code=403)
        blocked.raw.retries.history = (RequestHistory("GET", "/", None, 503, None),)
        mock_get.side_effect = [blocked, MagicMock(status_code=200)]
        mock_preview.return_value = ("Title", "Desc", "/og.png")
        mock_image.return_value = Preview("https://example.com/og.png", "picture")
        assert _fetch_preview("https://example.com").retries == ("503",)


class TestLocalImage:

    def test_webp_served_as_it_is(self, tmp_path):
        path = tmp_path / "cover.webp"
        path.write_bytes(_image_bytes(300, 400, "WEBP"))
        preview = _local_image(str(path))
        assert preview == Preview(str(path), "picture")
        assert preview.data == path.read_bytes()
        assert preview.path == "assets/awesome-list/images/cover.webp"
        assert preview.size == (300, 400)

    def test_not_an_image(self, tmp_path):
        (tmp_path / "cover.webp").write_bytes(b"<html>")
        with pytest.raises(ConfigurationError, match="can't read .*cover.webp"):
            _local_image(str(tmp_path / "cover.webp"))


class TestDomainLabel:

    @pytest.mark.parametrize(
        "url, label",
        [
            ("https://www.example.com/page", "example.com"),
            ("https://lab.example.org", "lab.example.org"),
            ("https://github.com/owner/repo#readme", "github.com/owner"),
            ("https://github.com", "github.com"),
        ],
    )
    def test_label(self, url, label):
        assert _domain_label(url) == label


# ---------------------------------------------------------------------------
# Rendered markup
# ---------------------------------------------------------------------------


class TestRenderedEntries:

    def test_entry_with_picture(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview("https://example.com/og.png", "picture")
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert '<ul class="awesome-list awesome-list--media">' in html
        assert '<li class="awesome-entry" data-image="picture">' in html
        assert 'class="awesome-entry__media" href="https://example.com"' in html
        assert '<img alt="" loading="lazy" src="https://example.com/og.png"' in html
        assert '<a class="awesome-entry__title" href="https://example.com">Example</a>' in html
        assert '<span class="awesome-entry__domain">example.com</span>' in html
        assert '<span class="awesome-entry__desc">An example site.</span>' in html

    def test_shrunk_picture_served_by_the_site(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = SHRUNK
        plugin.page_url = "about/"
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert f'src="../{THUMBNAIL}"' in html

    def test_entry_without_image(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview()
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert 'data-image="none"' in html
        assert "awesome-entry__media" not in html

    def test_favicon_path_is_relative_to_page(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview()
        plugin.favicons["example.com"] = b"png"
        plugin.page_url = "about/"
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert 'src="../assets/awesome-list/favicons/example.com.png"' in html

    def test_favicon_in_title(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview()
        plugin.favicons["example.com"] = b"png"
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert (
            '<a class="awesome-entry__title" href="https://example.com"><img alt="" '
            'class="awesome-entry__favicon" loading="lazy" '
            'src="assets/awesome-list/favicons/example.com.png" />Example</a>'
        ) in html

    def test_initial_when_no_favicon(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview()
        plugin.favicons["example.com"] = None
        html = _render(plugin, "- [example](https://example.com) - An example site.")

        assert '<span aria-hidden="true" class="awesome-entry__icon">E</span>' in html

    def test_markdown_in_description(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        html = _render(plugin, "- [A](https://a.example.com) - Works with [B](https://b.example.com).")

        assert (
            '<span class="awesome-entry__desc">Works with '
            '<a href="https://b.example.com">B</a>.</span>'
        ) in html

    def test_sub_entries(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        text = (
            "- [A](https://a.example.com) - Main entry.\n"
            "\t- [A Beta](https://a.example.com/beta) - Beta version.\n"
        )
        html = _render(plugin, text)

        assert '<li class="awesome-entry__sub">' in html
        assert '<a href="https://a.example.com/beta">A Beta</a>' in html
        assert '<span class="awesome-entry__sub-desc">Beta version.</span>' in html

    def test_media_sub_entries_follow_their_entry(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        plugin.favicons["a.example.com"] = b"png"
        text = (
            "- [A](https://a.example.com) - Main entry.\n"
            "\t- [A Beta](https://a.example.com/beta) - Beta version.\n"
            "- [B](https://a.example.com/b) - Next entry.\n"
        )
        plugin.previews["https://a.example.com/b"] = Preview()
        html = _render(plugin, text)

        entry_end = html.index("</li>", html.index("awesome-entry__desc"))
        row = html.index('<li class="awesome-subs"><ul aria-label="Related to A" class="awesome-entry__subs">')
        assert entry_end < row < html.index(">B</a>")
        assert '<a href="https://a.example.com/beta"><img alt="" class="awesome-entry__favicon"' in html

    def test_index_sub_entries_stay_in_their_entry(self):
        plugin = _make_plugin(default_style="index")
        plugin.previews["https://a.example.com"] = Preview()
        text = (
            "- [A](https://a.example.com) - Main entry.\n"
            "\t- [A Beta](https://a.example.com/beta) - Beta version.\n"
        )
        html = _render(plugin, text)

        assert '<ul class="awesome-entry__subs">' in html
        assert 'class="awesome-subs"' not in html
        # Index lists hide the description, so it's the tooltip
        assert '<a href="https://a.example.com/beta" title="Beta version.">A Beta</a>' in html

    def test_nested_sub_entries_kept_out_of_description(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        text = (
            "- [A](https://a.example.com) - Main entry.\n"
            "\t- [A Beta](https://a.example.com/beta) - Beta version.\n"
            "\t\t- [A Beta Docs](https://a.example.com/beta/docs) - Docs.\n"
        )
        html = _render(plugin, text)

        assert '<span class="awesome-entry__sub-desc">Beta version.</span>' in html
        assert '<li><a href="https://a.example.com/beta/docs">A Beta Docs</a> - Docs.</li>' in html

    def test_entry_without_description(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        plugin.previews["https://b.example.com"] = Preview()
        text = "- [A](https://a.example.com) - Entry A.\n- [B](https://b.example.com)\n"
        html = _render(plugin, text)

        assert html.count('<li class="awesome-entry" data-image="none">') == 2
        assert html.count("awesome-entry__desc") == 1

    def test_links_after_the_title_become_the_description(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        html = _render(plugin, "- [A](https://a.example.com) [[Part 2](https://a.example.com/2)]\n")

        assert '<span class="awesome-entry__desc">[<a href="https://a.example.com/2">Part 2</a>]</span>' in html

    def test_image_links_are_not_entries(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview()
        text = "- [![badge](https://img.example.com/badge.svg)](https://example.com) Follow us.\n"
        assert _render(plugin, text) == markdown.markdown(text)

    def test_loose_list(self):
        plugin = _make_plugin()
        plugin.previews["https://a.example.com"] = Preview()
        plugin.previews["https://b.example.com"] = Preview()
        text = "- [A](https://a.example.com) - Entry A.\n\n- [B](https://b.example.com) - Entry B.\n"
        html = _render(plugin, text)

        assert html.count('<li class="awesome-entry" data-image="none">') == 2
        assert '<span class="awesome-entry__desc">Entry B.</span>' in html
        assert "<p>" not in html

    def test_section_styles(self):
        plugin = _make_plugin(section_styles={"libraries": "index"})
        plugin.previews["https://a.example.com"] = Preview()
        plugin.previews["https://b.example.com"] = Preview()
        text = (
            "## Editors\n\n- [A](https://a.example.com) - Editor.\n\n"
            "## Libraries\n\n- [B](https://b.example.com) - Library.\n"
        )
        html = _render(plugin, text)

        editors, libraries = html.split('<h2 id="libraries">')
        assert "awesome-list--media" in editors
        assert "awesome-list--index" in libraries

    def test_image_from_the_option(self):
        plugin = _make_plugin(images={"https://example.com": COVER})
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert (
            '<img alt="" height="400" loading="lazy" '
            'src="assets/awesome-list/images/a.webp" width="300" />'
        ) in html

    def test_shelf_puts_the_details_in_one_element(self):
        plugin = _make_plugin(default_style="shelf", images={"https://example.com": COVER})
        text = "- [Book](https://example.com) - A book.\n\t- [Part 2](https://example.com/2) - 2.\n"
        html = _render(plugin, text)

        assert '<ul class="awesome-list awesome-list--shelf">' in html
        details = html[html.index('<div class="awesome-entry__details">'):]
        assert details.index("awesome-entry__header") < details.index("awesome-entry__desc")
        assert details.index("awesome-entry__desc") < details.index("awesome-entry__subs")
        assert html.index("awesome-entry__media") < html.index("awesome-entry__details")

    def test_shelf_ignores_the_preview(self, caplog):
        plugin = _make_plugin(default_style="shelf")
        plugin.previews["https://example.com"] = Preview("https://example.com/og.png", "picture")
        html = _render(plugin, "- [Book](https://example.com) - A book.")

        assert 'data-image="none"' in html
        assert "og.png" not in html
        assert 'images for "Book": https://example.com' in caplog.text

    def test_entries_without_preview_data_unchanged(self):
        plugin = _make_plugin()
        text = "- [Example](https://example.com) - An example site."
        assert _render(plugin, text) == markdown.markdown(text)

    def test_plain_lists_unchanged(self):
        plugin = _make_plugin()
        text = "- plain item\n- [Contents](#contents)"
        assert _render(plugin, text) == markdown.markdown(text)


# ---------------------------------------------------------------------------
# MkDocs events
# ---------------------------------------------------------------------------


@patch("awesome_list._fetch_favicon")
@patch("awesome_list._fetch_preview")
class TestOnPageMarkdown:

    def test_no_entries(self, mock_preview, mock_favicon):
        plugin = _make_plugin()
        md = "# Hello\n\n- plain item"
        assert plugin.on_page_markdown(md) == md
        mock_preview.assert_not_called()

    def test_fetches_previews_and_favicons(self, mock_preview, mock_favicon):
        mock_preview.return_value = Preview("https://example.com/og.png", "picture")
        mock_favicon.return_value = b"png"
        plugin = _make_plugin()
        md = (
            "- [A](https://example.com/a) - Description A\n"
            "- [B](https://www.example.com/b) - Description B\n"
            "\t- [Sub](https://example.com/sub) - Not fetched"
        )

        assert plugin.on_page_markdown(md, page=SimpleNamespace(url="about/")) == md
        assert set(plugin.previews) == {"https://example.com/a", "https://www.example.com/b"}
        assert plugin.favicons == {"example.com": b"png"}
        assert plugin.page_url == "about/"

    def test_only_web_links_are_entries(self, mock_preview, mock_favicon):
        mock_preview.return_value = Preview()
        plugin = _make_plugin()
        md = (
            "- [![badge](https://img.example.com/badge.svg)](https://example.com/repo)\n"
            "- [Section](#section)\n"
            "- [Title only](https://example.com/title)\n"
            "- [Spaced](https://example.com/spaced ) - Space before the bracket.\n"
        )
        plugin.on_page_markdown(md)

        assert set(plugin.previews) == {"https://example.com/title", "https://example.com/spaced"}

    def test_images_from_the_option_not_fetched(self, mock_preview, mock_favicon):
        mock_favicon.return_value = b"png"
        plugin = _make_plugin(images={"https://example.com/a": COVER})
        plugin.on_page_markdown("- [A](https://example.com/a) - Description A")

        mock_preview.assert_not_called()
        assert plugin.favicons == {"example.com": b"png"}

    def test_urls_fetched_once(self, mock_preview, mock_favicon):
        mock_preview.return_value = Preview()
        plugin = _make_plugin()
        md = "- [A](https://example.com) - Description A"
        plugin.on_page_markdown(md)
        plugin.on_page_markdown(md)

        assert mock_preview.call_count == 1
        assert mock_favicon.call_count == 1


def test_summary_groups_entries_by_problem():
    plugin = _make_plugin()
    plugin.previews.update({
        "https://a.example.com": Preview("https://a.example.com/og.png", "picture"),
        "https://b.example.com": Preview("https://b.example.com/og.png", "logo", retries=("429",)),
        "https://c.example.com": Preview(problem="Page returned 403"),
        "https://d.example.com": Preview(problem="No preview image on the page"),
        "https://e.example.com": Preview(problem="Page returned 403", retries=("timeout",)),
    })
    plugin.favicons.update({"a.example.com": b"png", "b.example.com": None})
    summary = plugin._summary(sorted(plugin.previews), ["a.example.com", "b.example.com"])
    assert summary.splitlines() == [
        "[AwesomeList] 5 previews: 1 pictures, 1 logos, 3 without an image. "
        "Favicons for 1 of 2 sites.",
        "  Page returned 403 (2):",
        "    https://c.example.com",
        "    https://e.example.com (after timeout)",
        "  No preview image on the page (1):",
        "    https://d.example.com",
        "  Found after retrying (1), past 429 x1:",
        "    https://b.example.com (after 429)",
    ]


def _mkdocs_config(extra=None, config_file_path="mkdocs.yml"):
    return SimpleNamespace(
        markdown_extensions=["toc"],
        extra_css=["css/theme.css"],
        extra=extra or {},
        config_file_path=config_file_path,
    )


def test_on_config_registers_extension_and_css():
    plugin = AwesomeList()
    config = _mkdocs_config()
    plugin.on_config(config)

    assert isinstance(config.markdown_extensions[-1], AwesomeListExtension)
    assert config.extra_css == ["assets/awesome-list/awesome-list.css", "css/theme.css"]
    assert plugin.config["default-style"] == "media"


def test_on_config_reads_options_from_extra():
    plugin = AwesomeList()
    options = {"default-style": "index", "section-styles": {"libraries": "media"}}
    plugin.on_config(_mkdocs_config({"awesome_list": options}))

    assert plugin.config["default-style"] == "index"
    assert plugin.config["section-styles"] == {"libraries": "media"}


def test_on_config_loads_images_next_to_the_config(tmp_path):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "a.webp").write_bytes(_image_bytes(300, 400, "WEBP"))
    options = {"images": {"https://example.com": "images/a.webp"}}
    plugin = AwesomeList()
    plugin.on_config(_mkdocs_config({"awesome_list": options}, str(tmp_path / "mkdocs.yml")))

    path = str(tmp_path / "images" / "a.webp")
    assert plugin.previews["https://example.com"] == Preview(path, "picture")


def test_on_config_rejects_missing_images(tmp_path):
    options = {"images": {"https://example.com": "images/missing.webp"}}
    config = _mkdocs_config({"awesome_list": options}, str(tmp_path / "mkdocs.yml"))
    with pytest.raises(ConfigurationError, match="missing.webp' isn't an existing file"):
        AwesomeList().on_config(config)


def test_on_config_rejects_images_with_the_same_file_name(tmp_path):
    for folder in ("a", "b"):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "cover.webp").write_bytes(_image_bytes(300, 400, "WEBP"))
    images = {"https://a.example.com": "a/cover.webp", "https://b.example.com": "b/cover.webp"}
    config = _mkdocs_config({"awesome_list": {"images": images}}, str(tmp_path / "mkdocs.yml"))
    with pytest.raises(ConfigurationError, match="same name"):
        AwesomeList().on_config(config)


def test_on_config_rejects_invalid_options():
    with pytest.raises(ConfigurationError, match="default-style"):
        AwesomeList().on_config(_mkdocs_config({"awesome_list": {"default-style": 1}}))


def test_on_post_build_writes_assets(tmp_path):
    plugin = _make_plugin()
    plugin.favicons = {"example.com": b"png", "no-icon.com": None}
    plugin.previews = {
        "https://a.example.com": SHRUNK,
        "https://b.example.com": Preview("https://b.example.com/logo.svg", "logo"),
        "https://c.example.com": COVER,
    }
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))

    assets = tmp_path / "assets" / "awesome-list"
    assert (assets / "awesome-list.css").is_file()
    assert (assets / "favicons" / "example.com.png").read_bytes() == b"png"
    assert not (assets / "favicons" / "no-icon.com.png").exists()
    assert sorted(p.name for p in (assets / "thumbnails").iterdir()) == ["a.webp", "index.html"]
    assert (assets / "thumbnails" / "a.webp").read_bytes() == b"og"
    assert (assets / "images" / "a.webp").read_bytes() == b"webp"


def test_on_post_build_warns_about_unused_images(tmp_path, caplog):
    gone = Preview("images/gone.webp", "picture", b"gone", "assets/awesome-list/images/gone.webp")
    plugin = _make_plugin(images={"https://a.example.com": COVER, "https://gone.example.com": gone})
    plugin.names = {"https://a.example.com": "A"}
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))

    assert "no entry links to https://gone.example.com" in caplog.text
    assert "https://a.example.com" not in caplog.text


def test_thumbnails_page_lists_card_images_in_list_order(tmp_path):
    plugin = _make_plugin()
    plugin.names = {
        "https://b.example.com": "Logo",
        "https://a.example.com": "A & B",
        "https://c.example.com": "No image",
        "https://d.example.com": "Book",
    }
    plugin.previews = {
        "https://a.example.com": SHRUNK,
        "https://b.example.com": Preview("https://b.example.com/logo.svg", "logo"),
        "https://c.example.com": Preview(),
        "https://d.example.com": COVER,
    }
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))
    page = (tmp_path / "assets" / "awesome-list" / "thumbnails" / "index.html").read_text()

    assert '<meta name="robots" content="noindex, nofollow' in page
    assert page.index('src="https://b.example.com/logo.svg"') < page.index('src="a.webp"')
    assert ">A &amp; B</a>" in page
    assert "No image" not in page
    assert 'src="../images/a.webp"' in page


# ---------------------------------------------------------------------------
# The real sites, to catch a change to the formats _known_image_urls relies on
# ---------------------------------------------------------------------------

HD_VIDEO = "https://www.youtube.com/watch?v=teALLngESw0"
NON_HD_VIDEO = "https://www.youtube.com/watch?v=Y9WXdobs_vU"
REPOSITORY = "https://github.com/microbit-foundation/microbit-fs"


def _page_image(url):
    resp = _get(url)
    if resp.status_code == 429:
        pytest.skip(f"{url} was rate limited, so its preview tag couldn't be checked")
    assert resp.ok, f"{url} returned {resp.status_code}, so its preview tag couldn't be checked"
    return web_preview(url, content=resp.text)[2]


def _assert_picture(image_url, site):
    preview = _fetch_image(image_url)
    if preview.problem == "Image returned 429":
        pytest.skip(f"{site} rate limited the request, so its format couldn't be checked")
    assert preview.image_kind == "picture", (
        f"{site}'s preview image URL format may have changed: {image_url} gave no picture "
        f"({preview.problem}). Update _known_image_urls in awesome_list.py to the format the "
        "site's pages use in their og:image tag."
    )


@pytest.mark.network
class TestKnownImageFormats:

    def test_youtube_hd_video(self):
        _assert_picture(_known_image_urls(HD_VIDEO)[0], "YouTube")

    def test_youtube_video_without_hd(self):
        maxres, hq = _known_image_urls(NON_HD_VIDEO)
        assert not _fetch_image(maxres).image, (
            f"{maxres} now gives a picture for a video without HD, so YouTube may have changed "
            "which thumbnails it makes; check the order in _known_image_urls in awesome_list.py."
        )
        _assert_picture(hq, "YouTube")

    @pytest.mark.parametrize("url", [HD_VIDEO, NON_HD_VIDEO])
    def test_youtube_page_shares_the_same_image(self, url):
        image = _page_image(url)
        if not image:
            pytest.skip("YouTube left the preview tags out, as it does for some servers")
        assert image.split("?")[0] in _known_image_urls(url), (
            f"YouTube's page shares {image}, which isn't one of the URLs _known_image_urls in "
            "awesome_list.py builds, so update it to this format."
        )

    def test_github_repository(self):
        _assert_picture(_known_image_urls(REPOSITORY)[0], "GitHub")

    def test_github_page_shares_the_same_image(self):
        image = _page_image(REPOSITORY)
        expected = re.escape(_known_image_urls(REPOSITORY)[0]).replace("/1/", "/[0-9a-f]+/")
        assert image and re.fullmatch(expected, image, re.IGNORECASE), (
            f"GitHub's page shares {image}, which doesn't match the URL _known_image_urls in "
            "awesome_list.py builds, so update it to this format."
        )
