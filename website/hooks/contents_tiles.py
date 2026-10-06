"""
content.html shows the `contents_tiles` section (mkdocs.yml) as tiles in place of its list, so
anything else under that heading never reaches the site. This warns about it during the build.
"""

import logging
import re

log = logging.getLogger("mkdocs.hooks.contents_tiles")


def on_page_content(html: str, page, config, **kwargs) -> str:
    section_id = config.theme.get("contents_tiles")
    if not section_id or 'class="awesome-list' not in html:
        return html
    section = re.search(r'<h2 id="%s">.*?</h2>(.*?)(?=<h2|$)' % re.escape(section_id), html, re.S)
    if section:
        rest = re.sub(r"<ul>.*?</ul>", "", section.group(1), count=1, flags=re.S)
        if re.sub(r"<[^>]+>", "", rest).strip():
            log.warning("%s: the '%s' section shows as tiles, so this under its heading is left out: %s",
                        page.file.src_uri, section_id, rest.strip()[:120])
    return html
