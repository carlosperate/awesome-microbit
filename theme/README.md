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
- **`css/extend.css`**: Restored Bootstrap's left gutter on the main container below 768px, where the sidebar is hidden, so the content no longer touches the left edge on phones.
- **`base.html`**: Below 768px the sidebar is hidden and its table of contents is at the end of the navbar menu instead. The navbar has no "Home" entry, as the site name links there, and the repository icon gets a label in the collapsed menu, like the theme toggle.
- **`js/awesome-microbit.js`**: Closes the navbar menu before jumping to an entry of its table of contents, as the open menu pushes the page down.
- **`js/base.js`**: `applyTopPadding()` also sets the sidebar's height from the navbar's, so it reaches the bottom of the screen when the navbar is collapsed.
- **`css/extend.css`**: Heading spacing: more space above `h2` than `h3`, an `h3` that scales with the screen width and has a regular weight, a responsive `h1` that fits on one line on phones and tablets, and space between headings and the navbar when jumping to them. The sidebar fills its column on pages with a short table of contents, its wrapped entries have tighter lines, and hovering an entry changes its colour instead of making it bold, which re-wrapped long entries. Inline code has rounded corners and the content more space at the bottom.
- **`css/awesome-microbit.css`**: Code in card titles (the Community handles) drops its box and link colour, and index lists sit as close to their heading as cards.
- **`css/extend.css`**: The site name in the navbar stays white and glows in the menu's hover purple on hover and keyboard focus, instead of turning the dark link hover colour, which was hard to read on the navbar.
