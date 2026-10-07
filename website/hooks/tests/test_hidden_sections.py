"""Tests for the hidden_sections MkDocs hook."""

import pytest

from hidden_sections import on_page_markdown

MARKDOWN = """# Title

## 🤷 Miscellaneous

- [Entry](https://example.com) - Description.

## ⚖️ License

[![CC0](https://example.com/cc0.svg)](https://example.com)

### Notes

Disclaimer.

## Later

Text.
"""


def config(hidden):
    return {"extra": {"hidden_sections": hidden}}


def test_hides_a_section_and_its_subsections():
    result = on_page_markdown(MARKDOWN, config(["license"]))
    assert "License" not in result
    assert "Disclaimer" not in result
    assert "## 🤷 Miscellaneous" in result
    assert "## Later\n\nText.\n" in result


@pytest.mark.parametrize("hidden", [None, [], ["contents"]])
def test_leaves_the_markdown_alone(hidden):
    assert on_page_markdown(MARKDOWN, config(hidden)) == MARKDOWN


def test_only_hides_sections():
    markdown = "## Tools\n\n### License\n\nKept.\n"
    assert on_page_markdown(markdown, config(["license"])) == markdown


def test_ignores_headings_in_code_blocks():
    markdown = "## License\n\n```python\n## Later\n```\n\nHidden.\n\n## Kept\n\n```\n## License\n```\n"
    assert on_page_markdown(markdown, config(["license"])) == "## Kept\n\n```\n## License\n```\n"


def test_without_the_option():
    assert on_page_markdown(MARKDOWN, {"extra": {}}) == MARKDOWN
