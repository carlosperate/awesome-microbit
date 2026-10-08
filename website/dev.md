# Developer Documentation

Run these commands from this `website/` folder. The site's pages, `README.md`, `contributing.md`
and `code-of-conduct.md`, are at the repository root.

## Install

Install the dependencies in a `.venv`:

```bash
uv sync
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install --group dev
```

## Build

Build the site into `site/`:

```bash
uv run python mkdocs-build.py
```

```bash
source .venv/bin/activate
python mkdocs-build.py
```

## Serve

```bash
python -m http.server 8000 --directory site
```

## CSS Screen sizes

- Phone: below 576px
- Small tablet: from 576px to 767px
- Tablet: from 768px to 991px 
- Small desktop: from 992px to 1199px
- Desktop: from 1200px to 1399px
- Large desktop: from 1400px

## Book covers

The Books section shows each book's cover on a shelf. The covers are prepared by hand, as a page's
preview picture isn't always the cover, so a new book needs one:

1. Find the cover on the publisher's page, or on Open Library, as large as possible.
2. Crop it to the cover if it's part of a bigger picture, and resize it to 400px tall.
3. Save it in `images/` as WebP (the smallest), named after the book, e.g. `images/micro-bit-recipes.webp`.
4. Add the book's link and the file under `images:` in `mkdocs.yml`, in the README's order.

Until then the book gets a plain cover, and the build warns about it.

## Test

```bash
uv run pytest
```

```bash
source .venv/bin/activate
python -m pytest
```
