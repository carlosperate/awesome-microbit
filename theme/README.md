# MkDocs Theme

Based on the default MkDocs theme, with custom CSS overrides in `extend.css`.

Updated to commit [2862536793b3c67d9d83c33e0dd6d50a791928f8](https://github.com/mkdocs/mkdocs/tree/2862536793b3c67d9d83c33e0dd6d50a791928f8/mkdocs/themes/mkdocs)
from 20th October 2025.

### Custom Modifications Since Import
- **`css/extend.css`**: Added a sticky Table of Contents sidebar with internal scrolling, hidden scrollbar until hover, and active state highlights for the active scrollspy element (`.nav-link.active`).
- **`js/base.js`**: Replaced Bootstrap's native ScrollSpy with a custom implementation to properly track layout hashes matching emojis inside IDs (since MkDocs encodes emojis in anchors).
- **`base.html`**: Updated the repo link in the navbar to show only the icon (GitHub, GitLab, or Bitbucket) without text.
- **`css/awesome-microbit.css`**: Awesome micro:bit colours and details for the awesome-list plugin cards, on top of the plugin's default layout, for light and dark mode. Each section of a list page gets its own hue, cards lift slightly on hover while the picture's colours bleed out of the thumbnail towards the pointer, and index lists use two columns where there is room.
- **`js/awesome-microbit.js`**: Sets each card picture as its own blurred backdrop and hover glow once it loads, moves the glow with the pointer, and switches a card to its favicon when its image fails to load in the browser.
- **`base.html`**: Loads `css/awesome-microbit.css` and `js/awesome-microbit.js` in the `<head>`, after `extra_css` so the CSS overrides the plugin's default card styles.
- **`content.html`**: On pages with awesome lists, wraps each `h2` section in a `<section class="awesome-section">` with its number in `--awesome-section`, used for the section colours.
- **`css/extend.css`**: Restored Bootstrap's left gutter on the main container below 768px, where the sidebar stacks above the content, so the content no longer touches the left edge on phones.
