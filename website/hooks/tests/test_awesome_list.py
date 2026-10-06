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
    USER_AGENTS,
    Preview,
    _domain_label,
    _fetch_image,
    _fetch_preview,
    _get,
    _image_filename,
    _image_kind,
    _local_image,
    _resolve_image_url,
)


def _png_bytes(width, height):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height)).save(buffer, "PNG")
    return buffer.getvalue()


def _webp_bytes(width, height):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height)).save(buffer, "WEBP")
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
COVER = Preview("images/a.webp", "picture", b"webp", (300, 400))


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


@patch("awesome_list.SESSION.get")
class TestFetchImage:

    @pytest.mark.parametrize(
        "size, shrunk",
        [((1200, 630), (600, 315)), ((600, 1200), (157, 315)), ((4000, 1000), (600, 150))],
    )
    def test_picture_shrunk_keeping_its_ratio(self, mock_get, size, shrunk):
        mock_get.return_value = _image_response(body=_png_bytes(*size))
        preview = _fetch_image("https://example.com/og.png")
        assert preview == Preview("https://example.com/og.png", "picture")
        assert _webp_size(preview.data) == shrunk

    def test_logo_keeps_its_size(self, mock_get):
        mock_get.return_value = _image_response(body=_png_bytes(180, 180))
        preview = _fetch_image("https://example.com/icon.png")
        assert preview == Preview("https://example.com/icon.png", "logo")
        assert _webp_size(preview.data) == (180, 180)

    def test_photo_rotated_by_its_exif_orientation(self, mock_get):
        exif = Image.Exif()
        exif[0x0112] = 6  # Orientation: rotate 90°
        buffer = io.BytesIO()
        Image.new("RGB", (300, 600)).save(buffer, "JPEG", exif=exif)
        mock_get.return_value = _image_response(content_type="image/jpeg", body=buffer.getvalue())
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
        assert _fetch_image("https://example.com/logo.svg") == Preview()

    def test_unreadable_image_format_is_linked(self, mock_get):
        mock_get.return_value = _image_response(content_type="image/jxl", body=b"...")
        preview = _fetch_image("https://example.com/img.jxl")
        assert preview == Preview("https://example.com/img.jxl", "picture")
        assert preview.data is None

    def test_http_error(self, mock_get):
        mock_get.return_value = _image_response(status=404)
        assert _fetch_image("https://example.com/missing.png") == Preview()

    def test_network_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("refused")
        assert _fetch_image("https://example.com/img.png") == Preview()

    def test_empty_image(self, mock_get):
        mock_get.return_value = _image_response(body=b"")
        assert _fetch_image("https://example.com/og.png") == Preview()

    @patch("awesome_list.IMAGE_MAX_BYTES", 10)
    def test_image_too_big(self, mock_get):
        mock_get.return_value = _image_response(body=_png_bytes(1200, 630))
        assert _fetch_image("https://example.com/og.png") == Preview()

    def test_not_an_image(self, mock_get):
        mock_get.return_value = _image_response(content_type="text/html", body=b"<html>")
        assert _fetch_image("https://example.com/page") == Preview()


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
        assert _fetch_preview("https://example.com") == Preview()
        mock_image.assert_not_called()

    def test_malformed_image_url(self, mock_get, mock_preview, mock_image):
        mock_preview.return_value = ("Title", "Desc", "http://[broken")
        assert _fetch_preview("https://example.com") == Preview()
        mock_image.assert_not_called()

    def test_page_error(self, mock_get, mock_preview, mock_image):
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
        assert _fetch_preview("https://example.com") == Preview()
        mock_preview.assert_not_called()


class TestLocalImage:

    def test_webp_served_as_it_is(self, tmp_path):
        data = _webp_bytes(300, 400)
        (tmp_path / "cover.webp").write_bytes(data)
        preview = _local_image("cover.webp", str(tmp_path))
        assert preview == Preview("cover.webp", "picture")
        assert preview.data == data
        assert preview.size == (300, 400)

    def test_not_an_image(self, tmp_path):
        (tmp_path / "cover.webp").write_bytes(b"<html>")
        with pytest.raises(ConfigurationError, match="can't read cover.webp"):
            _local_image("cover.webp", str(tmp_path))

    def test_missing_file(self, tmp_path):
        with pytest.raises(ConfigurationError, match="can't read missing.webp"):
            _local_image("missing.webp", str(tmp_path))


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
        image_url = "https://example.com/og.png"
        plugin.previews["https://example.com"] = Preview(image_url, "picture", b"webp")
        plugin.page_url = "about/"
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert f'src="../assets/awesome-list/thumbnails/{_image_filename(image_url)}"' in html

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

    def test_image_from_the_option_instead_of_the_preview(self):
        plugin = _make_plugin()
        plugin.previews["https://example.com"] = Preview("https://example.com/og.png", "picture")
        plugin.images["https://example.com"] = COVER
        html = _render(plugin, "- [Example](https://example.com) - An example site.")

        assert (
            '<img alt="" height="400" loading="lazy" '
            'src="assets/awesome-list/books/a.webp" width="300" />'
        ) in html
        assert "og.png" not in html

    def test_shelf_puts_the_details_in_one_element(self):
        plugin = _make_plugin(default_style="shelf")
        plugin.images["https://example.com"] = COVER
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
        plugin = _make_plugin()
        plugin.images["https://example.com/a"] = Preview("images/a.webp", "picture", b"webp")
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
    (tmp_path / "images" / "a.webp").write_bytes(_webp_bytes(300, 400))
    options = {"images": {"https://example.com": "images/a.webp"}}
    plugin = AwesomeList()
    plugin.on_config(_mkdocs_config({"awesome_list": options}, str(tmp_path / "mkdocs.yml")))

    assert plugin.images["https://example.com"] == Preview("images/a.webp", "picture")


def test_on_config_rejects_images_with_the_same_file_name(tmp_path):
    for folder in ("a", "b"):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "cover.webp").write_bytes(_webp_bytes(300, 400))
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
        "https://a.example.com": Preview("https://a.example.com/og.png", "picture", b"webp"),
        "https://b.example.com": Preview("https://b.example.com/logo.svg", "logo"),
    }
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))

    assets = tmp_path / "assets" / "awesome-list"
    assert (assets / "awesome-list.css").is_file()
    assert (assets / "favicons" / "example.com.png").read_bytes() == b"png"
    assert not (assets / "favicons" / "no-icon.com.png").exists()
    thumbnail = _image_filename("https://a.example.com/og.png")
    assert (assets / "thumbnails" / thumbnail).read_bytes() == b"webp"
    files = sorted(p.name for p in (assets / "thumbnails").iterdir())
    assert files == sorted([thumbnail, "index.html"])


def test_on_post_build_writes_images_and_warns_about_unused_ones(tmp_path, caplog):
    plugin = _make_plugin()
    plugin.names = {"https://a.example.com": "A"}
    plugin.images = {
        "https://a.example.com": Preview("images/a.webp", "picture", b"cover"),
        "https://gone.example.com": Preview("images/gone.webp", "picture", b"gone"),
    }
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))

    assert (tmp_path / "assets" / "awesome-list" / "books" / "a.webp").read_bytes() == b"cover"
    assert "no entry links to https://gone.example.com" in caplog.text
    assert "https://a.example.com" not in caplog.text


def test_thumbnails_page_lists_card_images_in_list_order(tmp_path):
    plugin = _make_plugin()
    plugin.names = {
        "https://b.example.com": "Logo",
        "https://a.example.com": "A & B",
        "https://c.example.com": "No image",
    }
    plugin.previews = {
        "https://a.example.com": Preview("https://a.example.com/og.png", "picture", b"webp"),
        "https://b.example.com": Preview("https://b.example.com/logo.svg", "logo"),
        "https://c.example.com": Preview(),
    }
    plugin.names["https://d.example.com"] = "Book"
    plugin.images = {"https://d.example.com": Preview("images/book.webp", "picture", b"cover")}
    plugin.on_post_build(SimpleNamespace(site_dir=str(tmp_path)))
    page = (tmp_path / "assets" / "awesome-list" / "thumbnails" / "index.html").read_text()

    assert '<meta name="robots" content="noindex, nofollow' in page
    assert page.index('src="https://b.example.com/logo.svg"') < page.index(
        f'src="{_image_filename("https://a.example.com/og.png")}"'
    )
    assert ">A &amp; B</a>" in page
    assert "No image" not in page
    assert 'src="../books/book.webp"' in page
