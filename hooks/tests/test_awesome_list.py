"""Tests for the awesome_list MkDocs hook."""

import io
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import markdown
import pytest
import requests
from mkdocs.exceptions import ConfigurationError
from PIL import Image

from awesome_list import (
    AwesomeList,
    AwesomeListExtension,
    Preview,
    _domain_label,
    _fetch_preview,
    _image_kind,
    _probe_image,
    _resolve_image_url,
)


def _png_bytes(width, height):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height)).save(buffer, "PNG")
    return buffer.getvalue()


def _image_response(status=200, content_type="image/png", body=b""):
    resp = MagicMock(status_code=status, headers={"Content-Type": content_type})
    resp.raw.read.return_value = body
    resp.__enter__.return_value = resp
    return resp


def _make_plugin(default_style="media", section_styles=None):
    plugin = AwesomeList()
    plugin.config = {
        "debug-log": False,
        "default-style": default_style,
        "section-styles": section_styles or {},
    }
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


@patch("awesome_list.requests.get")
class TestProbeImage:

    def test_wide_image_is_picture(self, mock_get):
        mock_get.return_value = _image_response(body=_png_bytes(1200, 630))
        assert _probe_image("https://example.com/og.png") == "picture"

    def test_small_image_is_logo(self, mock_get):
        mock_get.return_value = _image_response(body=_png_bytes(180, 180))
        assert _probe_image("https://example.com/icon.png") == "logo"

    def test_svg_is_logo(self, mock_get):
        body = b'\n<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>'
        mock_get.return_value = _image_response(content_type="image/svg+xml", body=body)
        assert _probe_image("https://example.com/logo.svg") == "logo"

    def test_broken_svg(self, mock_get):
        body = b'?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"></svg>'
        mock_get.return_value = _image_response(content_type="image/svg+xml", body=body)
        assert _probe_image("https://example.com/logo.svg") is None

    def test_http_error(self, mock_get):
        mock_get.return_value = _image_response(status=404)
        assert _probe_image("https://example.com/missing.png") is None

    @patch("awesome_list.time.sleep")
    def test_rate_limited_then_ok(self, _mock_sleep, mock_get):
        mock_get.side_effect = [
            _image_response(status=429),
            _image_response(body=_png_bytes(1200, 630)),
        ]
        assert _probe_image("https://example.com/og.png") == "picture"

    def test_network_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("refused")
        assert _probe_image("https://example.com/img.png") is None

    def test_unreadable_image_format(self, mock_get):
        mock_get.return_value = _image_response(content_type="image/avif", body=b"...")
        assert _probe_image("https://example.com/img.avif") == "picture"

    def test_empty_image(self, mock_get):
        mock_get.return_value = _image_response(body=b"")
        assert _probe_image("https://example.com/og.png") is None

    def test_not_an_image(self, mock_get):
        mock_get.return_value = _image_response(content_type="text/html", body=b"<html>")
        assert _probe_image("https://example.com/page") is None


@patch("awesome_list._probe_image")
@patch("awesome_list.web_preview")
class TestFetchPreview:

    def test_image_found(self, mock_preview, mock_probe):
        mock_preview.return_value = ("Title", "Desc", "/og.png")
        mock_probe.return_value = "picture"
        result = _fetch_preview("https://example.com/page")
        assert result == Preview("https://example.com/og.png", "picture")

    def test_no_image(self, mock_preview, mock_probe):
        mock_preview.return_value = ("Title", "Desc", None)
        assert _fetch_preview("https://example.com") == Preview()
        mock_probe.assert_not_called()

    def test_broken_image(self, mock_preview, mock_probe):
        mock_preview.return_value = ("Title", "Desc", "https://example.com/og.png")
        mock_probe.return_value = None
        assert _fetch_preview("https://example.com") == Preview()

    def test_malformed_image_url(self, mock_preview, mock_probe):
        mock_preview.return_value = ("Title", "Desc", "http://[broken")
        assert _fetch_preview("https://example.com") == Preview()
        mock_probe.assert_not_called()

    def test_page_error(self, mock_preview, mock_probe):
        mock_preview.side_effect = Exception("timeout")
        assert _fetch_preview("https://example.com") == Preview()


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

        assert '<ul class="awesome-entry__subs">' in html
        assert '<li class="awesome-entry__sub">' in html
        assert '<a href="https://a.example.com/beta" title="Beta version.">A Beta</a>' in html
        assert '<span class="awesome-entry__sub-desc">Beta version.</span>' in html

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

    def test_urls_fetched_once(self, mock_preview, mock_favicon):
        mock_preview.return_value = Preview()
        plugin = _make_plugin()
        md = "- [A](https://example.com) - Description A"
        plugin.on_page_markdown(md)
        plugin.on_page_markdown(md)

        assert mock_preview.call_count == 1
        assert mock_favicon.call_count == 1


def _mkdocs_config(extra=None):
    return SimpleNamespace(
        markdown_extensions=["toc"], extra_css=["css/theme.css"], extra=extra or {}
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


def test_on_config_rejects_invalid_options():
    with pytest.raises(ConfigurationError, match="default-style"):
        AwesomeList().on_config(_mkdocs_config({"awesome_list": {"default-style": 1}}))


def test_on_post_build_writes_assets(tmp_path):
    plugin = _make_plugin()
    plugin.favicons = {"example.com": b"png", "no-icon.com": None}
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))

    assets = tmp_path / "assets" / "awesome-list"
    assert (assets / "awesome-list.css").is_file()
    assert (assets / "favicons" / "example.com.png").read_bytes() == b"png"
    assert not (assets / "favicons" / "no-icon.com.png").exists()
