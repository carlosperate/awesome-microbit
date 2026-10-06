"""Tests for the contents_tiles MkDocs hook."""

from types import SimpleNamespace

import pytest

from contents_tiles import on_page_content

PAGE = SimpleNamespace(file=SimpleNamespace(src_uri="README.md"))
CONFIG = SimpleNamespace(theme={"contents_tiles": "contents"})
NEXT_SECTION = '<h2 id="cad">CAD</h2><p>Intro</p><ul class="awesome-list"><li>Entry</li></ul>'


@pytest.mark.parametrize(
    "contents, warns",
    [
        ('<ul><li><a href="#cad">CAD</a></li></ul>', False),
        ('<p>Jump to:</p><ul><li><a href="#cad">CAD</a></li></ul>', True),
        ('<ul><li><a href="#cad">CAD</a></li></ul><ul><li>Second list</li></ul>', True),
    ],
)
def test_warns_about_content_besides_the_list(caplog, contents, warns):
    html = '<h2 id="contents">Contents</h2>' + contents + NEXT_SECTION
    assert on_page_content(html, PAGE, CONFIG) == html
    assert ("left out" in caplog.text) == warns
