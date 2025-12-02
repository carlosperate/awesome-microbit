#!/usr/bin/env python3
"""
Script to check for redirects in all URLs found in a Markdown file.
Uses async requests for fast parallel checking.
"""
# /// script
# requires-python = ">=3.11"
# dependencies = [ "httpx" ]
# ///
import argparse
import asyncio
import os
import re
import sys
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, Optional, Set

import httpx


def load_ignore_lists() -> Tuple[Set[str], Set[str]]:
    """
    Load ignore lists from exceptions.toml file.

    :returns: Tuple of sets (redirect_ignore, error_ignore)
    """
    script_dir = Path(__file__).parent
    exceptions_file = script_dir / "ignore.toml"
    if exceptions_file.exists():
        data = tomllib.loads(exceptions_file.read_text(encoding='utf-8'))
        return (set(data.get('redirect_ignore', {}).get('urls', [])),
                set(data.get('error_ignore', {}).get('urls', [])))
    return set(), set()


# Load ignore lists only once at module level
REDIRECT_IGNORE, ERROR_IGNORE = load_ignore_lists()


def should_ignore_redirect(url: str) -> bool:
    """Check if a URL redirect should be ignored based on exception list."""
    if url in REDIRECT_IGNORE:
        return True
    return any(ignore_domain in url for ignore_domain in REDIRECT_IGNORE)


def should_ignore_error(url: str) -> bool:
    """Check if a URL error should be ignored based on exception list."""
    if url in ERROR_IGNORE:
        return True
    return any(ignore_domain in url for ignore_domain in ERROR_IGNORE)


def extract_urls_from_markdown(text: str) -> List[str]:
    """
    Extract URLs from Markdown file, handling inline links and plain URLs,
    and intelligently trimming surrounding punctuation or brackets.
    Returns a list of unique URLs.
    """
    urls = []
    seen = set()

    # Match Markdown inline links: [text](URL)
    inline_link_pattern = re.compile(r'\[.*?\]\((https?://[^\s<>)]+)\)')
    for match in inline_link_pattern.finditer(text):
        url = match.group(1).rstrip('.,;:!?\'")')
        if url not in seen:
            urls.append(url)
            seen.add(url)

    # Match plain URLs (not already captured by inline links)
    url_pattern = re.compile(r'https?://[^\s<>]+')
    for match in url_pattern.finditer(text):
        url = match.group()
        start, end = match.start(), match.end()

        # Look at surrounding characters
        before = text[start-1] if start > 0 else ''
        after = text[end] if end < len(text) else ''

        # Trim enclosing parentheses, brackets, or braces if they appear to be outside the URL
        if after in [')', ']', '}'] and before in ['(', '[', '{']:
            url = url[:-1]

        # Trim common trailing punctuation
        url = url.rstrip('.,;:!?\'")')

        if url not in seen:
            urls.append(url)
            seen.add(url)

    return urls


@lru_cache()
def _split_lines(text: str) -> tuple[str, ...]:
    """Cache the split lines operation since we use the same text repeatedly."""
    return tuple(text.split('\n'))


def find_line_number(text: str, url: str) -> int:
    """Find the line number where a URL first appears in the text."""
    lines = _split_lines(text)
    for line_num, line in enumerate(lines, 1):
        if url in line:
            return line_num
    return 0


def create_github_line_link(line_num: int, markdown_file: str) -> str:
    """Create a GitHub link to a specific line in a file, or just the line number if not in GitHub Actions."""
    github_server = os.getenv('GITHUB_SERVER_URL', 'https://github.com')
    github_repo = os.getenv('GITHUB_REPOSITORY', '')
    github_sha = os.getenv('GITHUB_SHA', '')

    if github_repo and github_sha:
        file_link = f"{github_server}/{github_repo}/blob/{github_sha}/{markdown_file}?plain=1#L{line_num}"
        return f"[L{line_num}]({file_link})"
    else:
        return f"L{line_num}"


async def check_redirect(client: httpx.AsyncClient, url: str, index: int) -> Tuple[int, str, Optional[str], Optional[str]]:
    """
    Perform an async HEAD request to check if URL redirects.
    Returns tuple of (index, url, final_url or None, error or None).
    """
    try:
        # Try HEAD request first for speed
        resp = await client.head(url, follow_redirects=True, timeout=10.0)
        final_url = str(resp.url)
        if final_url != url:
            return (index, url, final_url, None)
        return (index, url, None, None)
    except (httpx.HTTPError, httpx.TimeoutException):
        # Try GET request if HEAD fails
        try:
            resp = await client.get(url, follow_redirects=True, timeout=10.0)
            final_url = str(resp.url)
            if final_url != url:
                return (index, url, final_url, None)
            return (index, url, None, None)
        except Exception as e:
            return (index, url, None, str(e))


async def check_all_redirects(urls: List[str]) -> List[Tuple[int, str, Optional[str], Optional[str]]]:
    """Check all URLs for redirects asynchronously."""
    async with httpx.AsyncClient() as client:
        tasks = [check_redirect(client, url, i) for i, url in enumerate(urls, 1)]
        results = await asyncio.gather(*tasks)
        return results


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description='Check for redirects in all URLs found in a Markdown file.'
    )
    parser.add_argument(
        'markdown_file',
        nargs='?',
        default='README.md',
        help='Path to the Markdown file to scan (default: README.md)'
    )
    parser.add_argument(
        '--fail-on-redirect',
        action='store_true',
        help='Fail if redirects are found (default: only fail on errors)'
    )
    return parser.parse_args()


def main():
    print_title = lambda msg: print(f"\n{'='*80}\n{msg}\n{'='*80}")
    gh_summary_file = os.getenv('GITHUB_STEP_SUMMARY')

    args = parse_cli_args()
    markdown_file = args.markdown_file
    fail_on_redirect = args.fail_on_redirect

    print_title(f"🔍 Extracting URLs from {markdown_file}...")
    try:
        text = Path(markdown_file).read_text(encoding='utf-8')
        urls = extract_urls_from_markdown(text)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
    print(f"Found {len(urls)} unique URLs")
    if not urls:
        print("No URLs found in the file.")
        sys.exit(0)

    print_title("🔗 Checking for redirects...")
    results = asyncio.run(check_all_redirects(urls))
    results.sort(key=lambda x: x[0])

    redirects = []
    errors = []
    ignored_redirects = []
    ignored_errors = []
    error_count = 0
    for index, url, final_url, error in results:
        print(f"{index}. {url}")
        if error:
            if should_ignore_error(url):
                print(f"\t⚠️  Error (ignored): {error}")
                ignored_errors.append((url, error))
            else:
                error_count += 1
                print(f"\t❌ Error: {error}")
                errors.append((url, error))
        if final_url:
            if should_ignore_redirect(url):
                print(f"\t↪️⚠️ (ignored) Redirects to: {final_url}")
                ignored_redirects.append((url, final_url))
            else:
                redirects.append((url, final_url))
                print(f"\t↪️  Redirects to: {final_url}")

    if ignored_redirects or ignored_errors:
        print_title(f"🫣  IGNORED EXCEPTIONS")
        if ignored_redirects:
            print(f"⚠️ Ignored {len(ignored_redirects)} redirect(s) (in exception list):\n")
            for url, final_url in ignored_redirects:
                print(f"  {url}\n    → {final_url}\n")
            print()
        if ignored_errors:
            print(f"⚠️ Ignored {len(ignored_errors)} error(s) (in exception list):\n")
            for url, error in ignored_errors:
                print(f"  {url}: {error}\n")
            print()

    print_title(f"↪️ SUMMARY OF REDIRECTS")
    if redirects:
        print(f"Found {len(redirects)} redirect(s)\n")
        if gh_summary_file:
            with open(gh_summary_file, 'a', encoding='utf-8') as f:
                f.write(f"## 🔗 URL Redirects Found ({len(redirects)})\n\n")
                for original, redirected in redirects:
                    f.write(f"- Original:\t{original}\n")
                    f.write(f"  Redirect:\t{redirected}\n")
                    line_num = find_line_number(text, original)
                    line_link = create_github_line_link(line_num, markdown_file)
                    f.write(f"  Line: {line_link}\n")
                f.write("\n")

        for original, redirected in redirects:
            line_num = find_line_number(text, original)
            print(f"Original:  {original}")
            print(f"Redirect:  {redirected}\n")
    else:
        print("✅ No redirects found!")

    print_title(f"‼️ ERRORS ENCOUNTERED")
    if error_count > 0:
        print(f"{error_count} URL(s) had errors during checking")
        if gh_summary_file:
            with open(gh_summary_file, 'a', encoding='utf-8') as f:
                f.write(f"## ❌ Errors Encountered ({error_count})\n\n")
                for url, error in errors:
                    line_num = find_line_number(text, url)
                    # Escape pipe characters in error message
                    line_link = create_github_line_link(line_num, markdown_file)
                    f.write(f"- Error for {url}: {error}\n  Line: {line_link}\n")
                f.write("\n")
        for url, error in errors:
            print(f"{url}\n  Error: {error}\n\n")
    else:
        print("✅ No errors encountered!")

    if error_count > 0 or (redirects and fail_on_redirect):
        sys.exit(1)


if __name__ == '__main__':
    main()
