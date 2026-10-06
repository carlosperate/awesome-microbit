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

## Test

```bash
uv run pytest
```

```bash
source .venv/bin/activate
python -m pytest
```
