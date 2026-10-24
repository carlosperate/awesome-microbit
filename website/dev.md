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

- Phone, test at 360×750: below 576px
- Small tablet, test at 744×1133: from 576px to 767px
- Tablet, test at 820×1180: from 768px to 991px
- Small desktop, test at 1024×768: from 992px to 1199px
- Desktop, test at 1280×800: from 1200px to 1399px
- Large desktop, test at 1440×900: from 1400px

## Book covers

The Books section shows each book's cover on a shelf. The covers are prepared by hand, as a page's
preview picture isn't always the cover, so a new book needs one:

1. Find the cover on the publisher's page, or on Open Library, as large as possible.
2. Crop it to the cover if it's part of a bigger picture, and resize it to 400px tall.
3. Save it in `images/books/` as WebP (the smallest), named after the book, e.g. `images/books/micro-bit-recipes.webp`.
4. Add the book's link and the file under `images:` in `mkdocs.yml`, in the README's order.

Until then the book gets a plain cover, and the build warns about it.

## Poster artwork

The Posters section shows each print in its own framed card, with two cards per row on phones.
Like Books, it uses local artwork rather than OpenGraph previews:

1. Visit the resource and download the actual poster or render the first page of its PDF.
   For a collection, choose one representative poster without adding extra list entries.
2. Keep the entire print and its aspect ratio. Resize it to fit 600×400px, without upscaling
   smaller originals, and save it in `images/posters/` as WebP at quality 80. This is twice the
   largest displayed size (about 300×200px), for sharp thumbnails on high-density screens.
3. Map the README entry's exact URL to this file under `images:` in `mkdocs.yml`.
4. Record its source and attribution in `images/posters/README.md`. Download signed image links
   while valid, as the site must serve a local copy after those links expire.

A poster without artwork still has its title, description and source link, with a favicon
placeholder. The build warns about missing artwork and never substitutes a social card.

## Blocked previews

Some sites put their pages behind a Cloudflare challenge, which only a browser can pass, so the
build can't fetch their previews and lists them as `Page returned 403` in its summary. Their
previews are saved in `images/previews/` instead:

1. Open the page in a browser and copy the `og:image` link from its source.
2. Download the image and shrink it to WebP as the build would, named after the site and the page:

   ```bash
   python -c "import sys; sys.path.insert(0, 'hooks'); from awesome_list import _shrink_image; open(sys.argv[2], 'wb').write(_shrink_image(open(sys.argv[1], 'rb').read())[1])" ~/Downloads/robots-buggy1.jpg images/previews/kitronik-robot-buggy.webp
   ```

3. Add the link and the file under `images:` in `mkdocs.yml`, after the Books covers.

## Test

```bash
uv run pytest
```

```bash
source .venv/bin/activate
python -m pytest
```
