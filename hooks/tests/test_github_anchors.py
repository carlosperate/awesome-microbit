"""Tests for the github_anchors MkDocs hook."""

import pytest

from github_anchors import on_page_markdown


@pytest.mark.parametrize(
    "markdown, expected",
    [
        ("[📐 CAD](#-cad)", "[📐 CAD](#cad)"),
        ("[©️ C/C++](#%EF%B8%8F-cc)", "[©️ C/C++](#cc)"),
        ("[🅰️ Accessibility](#🅰%EF%B8%8F-accessibility)", "[🅰️ Accessibility](#accessibility)"),
        ("[C & C++](#c--c)", "[C & C++](#c-c)"),
        ("[Python](#python)", "[Python](#python)"),
        ("[Site](https://example.com/#-top)", "[Site](https://example.com/#-top)"),
    ],
)
def test_github_anchors_rewritten(markdown, expected):
    assert on_page_markdown(markdown) == expected
