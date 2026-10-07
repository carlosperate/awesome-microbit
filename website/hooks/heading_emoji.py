"""
Screen readers announce a heading's emoji by name ("moai JavaScript and MakeCode"), so the emoji
the README starts its headings with are wrapped in a span hidden from them. The span also lets the
theme draw them with a colour emoji font.
"""

import re

# A heading's first word, followed by the rest of its text
HEADING_START = re.compile(r"(<h[1-6][^>]*>)([^\s<]+) ")


def _wrap_emoji(match: re.Match) -> str:
    # Like macros.html's title_emoji: a first word with no letters or digits in any script
    if any(character.isalnum() for character in match.group(2)):
        return match.group(0)
    return '%s<span class="heading-emoji" aria-hidden="true">%s</span> ' % match.groups()


def on_page_content(html: str, **kwargs) -> str:
    return HEADING_START.sub(_wrap_emoji, html)
