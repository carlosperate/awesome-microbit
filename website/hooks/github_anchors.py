"""
GitHub's heading anchors keep an emoji's leftovers and doubled hyphens (`#-cad`, `#c--c`),
MkDocs' ids drop them (`cad`, `c-c`). The README must keep GitHub's, so the in-page links are
rewritten in the copy MkDocs builds, before MkDocs checks them.
"""

import re
from urllib.parse import unquote

# An inline Markdown link to an anchor on the same page: [text](#anchor)
ANCHOR_LINK = re.compile(r"\]\(#([^)\s]+)\)")
# What an emoji leaves before the first hyphen: anything but letters and digits, in any script
GITHUB_PREFIX = re.compile(r"^\W*-")
HYPHENS = re.compile(r"-{2,}")


def _mkdocs_link(match: re.Match) -> str:
    anchor = unquote(match.group(1))
    mkdocs_anchor = HYPHENS.sub("-", GITHUB_PREFIX.sub("", anchor))
    if mkdocs_anchor == anchor:
        return match.group(0)
    return "](#" + mkdocs_anchor + ")"


def on_page_markdown(markdown: str, **kwargs) -> str:
    return ANCHOR_LINK.sub(_mkdocs_link, markdown)
