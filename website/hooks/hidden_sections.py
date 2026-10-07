"""
Leaves README sections out of the site, keyed by their `##` heading's anchor under
`extra: hidden_sections:` in mkdocs.yml, as the README must keep them for GitHub.
"""

import re

from markdown.extensions.toc import slugify

# Sections and the title above them, as only they can end a section
HEADING = re.compile(r"^(#{1,2})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def on_page_markdown(markdown: str, config, **kwargs) -> str:
    hidden = set(config["extra"].get("hidden_sections") or [])
    if not hidden:
        return markdown
    kept, hiding, fence = [], False, None
    for line in markdown.splitlines(keepends=True):
        # A `#` in a code block isn't a heading
        opening = FENCE.match(line)
        if fence:
            if opening and opening.group(1).startswith(fence):
                fence = None
        elif opening:
            fence = opening.group(1)
        else:
            heading = HEADING.match(line)
            if heading:
                hiding = len(heading.group(1)) == 2 and slugify(heading.group(2), "-") in hidden
        if not hiding:
            kept.append(line)
    return "".join(kept)
