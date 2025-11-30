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
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

import httpx


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
    """
    Check all URLs for redirects asynchronously.
    """
    async with httpx.AsyncClient() as client:
        tasks = [check_redirect(client, url, i) for i, url in enumerate(urls, 1)]
        results = await asyncio.gather(*tasks)
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Check for redirects in all URLs found in a Markdown file.'
    )
    parser.add_argument(
        'markdown_file',
        nargs='?',
        default='README.md',
        help='Path to the Markdown file to scan (default: README.md)'
    )
    args = parser.parse_args()
    markdown_file = args.markdown_file

    try:
        print(f"🔍 Extracting URLs from {markdown_file}...")
        urls = extract_urls_from_markdown(Path(markdown_file).read_text(encoding='utf-8'))
        print(f"Found {len(urls)} unique URLs")
    except FileNotFoundError:
        print(f"❌ Error: File '{markdown_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    if not urls:
        print("No URLs found in the file.")
        sys.exit(0)

    print_title = lambda s: print(f"\n{'='*80}\n{s}\n{'='*80}")

    print_title("🔗 Checking for redirects...")

    # Run async checks & store results by index
    results = asyncio.run(check_all_redirects(urls))
    results.sort(key=lambda x: x[0])

    redirects = []
    errors = []
    error_count = 0
    for index, url, final_url, error in results:
        print(f"{index}. {url}")
        if error:
            error_count += 1
            print(f"\t❌ Error: {error}")
            errors.append((url, error))
        elif final_url:
            redirects.append((url, final_url))
            print(f"\t↪️  Redirects to: {final_url}")

    print_title(f"📋 SUMMARY OF REDIRECTS")
    if redirects:
        print(f"Found {len(redirects)} redirect(s):\n")
        for original, redirected in redirects:
            print(f"Original:  {original}")
            print(f"Redirect:  {redirected}\n")
    else:
        print("✅ No redirects found!")

    print_title(f"❗ ERRORS ENCOUNTERED")
    if error_count > 0:
        print(f"{error_count} URL(s) had errors during checking")
        for url, error in errors:
            print(f"- {url}\n  Error: {error}\n")
    else:
        print("✅ No errors encountered!")

    if redirects or error_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
