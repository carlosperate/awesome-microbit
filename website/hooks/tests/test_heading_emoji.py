"""Tests for the heading_emoji MkDocs hook."""

import pytest

from heading_emoji import on_page_content


@pytest.mark.parametrize(
    "html, expected",
    [
        ('<h2 id="python">🐍 Python</h2>',
         '<h2 id="python"><span class="heading-emoji" aria-hidden="true">🐍</span> Python</h2>'),
        ('<h2 id="cc">©️ C/C++</h2>',
         '<h2 id="cc"><span class="heading-emoji" aria-hidden="true">©️</span> C/C++</h2>'),
        ('<h3 id="classroom">👩‍💻 Classroom Environments</h3>',
         '<h3 id="classroom"><span class="heading-emoji" aria-hidden="true">👩‍💻</span> Classroom Environments</h3>'),
        ('<h2 id="adding">Adding to this list</h2>', '<h2 id="adding">Adding to this list</h2>'),
        ('<h1 id="awesome-microbit">Awesome micro:bit</h1>', '<h1 id="awesome-microbit">Awesome micro:bit</h1>'),
        ('<h2 id="emoji">🐍</h2>', '<h2 id="emoji">🐍</h2>'),
        ('<p>🐍 Python</p>', '<p>🐍 Python</p>'),
    ],
)
def test_heading_emoji_hidden(html, expected):
    assert on_page_content(html) == expected
