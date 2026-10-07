# MkDocs hooks

Loaded from the `hooks:` list in `mkdocs.yml`.

- **`hidden_sections.py`**: Leaves the sections (`##` headings) listed under
  `extra: hidden_sections:` (by heading anchor) out of the site, along with their subsections.
- **`github_anchors.py`**: Rewrites the README's in-page links from GitHub's heading anchors
  (`#-cad`) to the ids MkDocs generates (`#cad`).
- **`awesome_list.py`**: Turns each awesome-list entry into a card with the linked page's
  preview image and favicon. Its default stylesheet is `awesome-list.css`.
- **`heading_emoji.py`**: Wraps the emoji a heading starts with in a span hidden from screen
  readers, which announce them by name.

The tests are in `tests/`:

```bash
pytest -v
```

## awesome_list

Entries are top-level list items that start with a web link, usually written as
`- [Name](url) - Description` (the description is optional). Indented sub-entries never get a
card of their own.

During the build the hook fetches each entry's OpenGraph image and the site's favicon, then
adds classes and that data to the list Markdown renders. Requests are retried on connection
errors, rate limits and server errors, and repeated with the hook's own user agent when a site
blocks Python's default one.

The site serves its own copy of each image, shrunk to fit 600x315 (three times the card's frame) and
saved as WebP, so huge originals and links that break later don't affect it. SVGs, and formats
Pillow can't read, still link the original.

An entry can have its own image instead of its page's preview, from the `images` option. The
site serves those as they are, and the build doesn't fetch the preview for them.

`assets/awesome-list/thumbnails/` on the built site shows every card image on one page, to check
them by eye. Nothing links to it, and it asks search engines not to index it.

### Options

Hooks take no options of their own, so they go under `extra:` in `mkdocs.yml`:

```yml
extra:
  awesome_list:
    debug-log: false
    # Card style for every list, added as an `awesome-list--<style>` class
    default-style: media
    # Per-section styles, keyed by the heading anchor
    section-styles:
      libraries: index
      books: shelf
    # Images to show instead of the page's preview, keyed by the entry's link, with paths
    # relative to mkdocs.yml
    images:
      "https://example.com/book": images/book.webp
```

The site serves them unchanged from `assets/awesome-list/images/`, under their own file names, so
two can't share a name. The build stops if one is missing or can't be read as an image, and warns
about images no entry links to.

`awesome-list.css` includes these styles:

- `media`: a card per entry, with the preview image on the left. In lists narrower
  than 600px the description goes under the image instead.
- `gallery`: the same cards as `media` (its lists get both classes), in columns with the preview
  image on top, for sections where the pictures matter most. Lists too narrow for two columns
  use the `media` layout.
- `index`: compact rows with the site's favicon, useful for long lists of repositories.
- `shelf`: covers side by side, like books on a shelf, with the details over the cover on hover,
  keyboard focus, or when a theme script adds `awesome-entry--open` (on touch screens, which can't
  hover). It only shows images from the `images` option, as a page's preview isn't always
  its cover: an entry without one gets a plain cover with its favicon, and a build warning.

Any other style name only adds its class, for the theme to style.

### Markup

```html
<ul class="awesome-list awesome-list--media">
  <li class="awesome-entry" data-image="picture">
    <a class="awesome-entry__media" href="…"><img src="…"></a>
    <span class="awesome-entry__icon"><img src="…"></span>
    <span class="awesome-entry__header">
      <a class="awesome-entry__title" href="…"><img class="awesome-entry__favicon" src="…">Name</a>
      <span class="awesome-entry__domain">example.com</span>
    </span>
    <span class="awesome-entry__desc">Description</span>
    <ul class="awesome-entry__subs">
      <li class="awesome-entry__sub">
        <a href="…" title="Description">Name</a>
        <span class="awesome-entry__sub-desc">Description</span>
      </li>
    </ul>
  </li>
</ul>
```

- `data-image` is `picture`, `logo` (200px or smaller) or `none` (no
  image, or it couldn't be loaded). `awesome-entry__media` is only there when
  there is an image.
- `awesome-entry__icon` holds the favicon, or the entry's initial when the
  site has none. The same favicon is also in the title, when there is one.
- The default CSS stretches the title link over the entry, so the whole card is
  one click target; other links in it stay clickable above it.
- `awesome-entry__subs` holds the indented sub-entries, if any.
- Images from the `images` option also have `width` and `height`, so the browser can lay them out
  before they load.
- In `shelf` lists, the header, description and sub-entries are in a
  `<div class="awesome-entry__details">`, after the icon.

The stylesheet, favicons, thumbnails and the `images` option's images are written to
`site/assets/awesome-list/`. The stylesheet comes
first in `extra_css`, and `theme/base.html` loads `css/awesome-microbit.css` after it, to override
its CSS custom properties or any rule.
