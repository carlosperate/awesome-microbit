"""GH Action entry point to post new entries to the Awesome micro:bit list.

It will post the same content to Twitter and BlueSky.

This script depends on environmental variables set for the Twitter
and BlueSky API access tokens.
It also depends on running with the Current Working Directory set to the
repository root.
"""

import os
import io
import re
import sys
import argparse
from urllib.parse import urljoin

from git import Repo
import tweepy
from atproto import Client, client_utils, models
import httpx

# Getting the Twitter secrets form local dev file or GH action secrets
try:
    from twitter_secrets import (
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
    )
except ImportError:
    TWITTER_CONSUMER_KEY = os.environ.get("INPUT_TWITTER_CONSUMER_KEY", None)
    TWITTER_CONSUMER_SECRET = os.environ.get(
        "INPUT_TWITTER_CONSUMER_SECRET", None
    )
    TWITTER_ACCESS_TOKEN = os.environ.get("INPUT_TWITTER_ACCESS_TOKEN", None)
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get(
        "INPUT_TWITTER_ACCESS_TOKEN_SECRET", None
    )
try:
    from bluesky_secrets import (
        BLUESKY_USERNAME,
        BLUESKY_TOKEN,
    )
except ImportError:
    BLUESKY_USERNAME = os.environ.get("INPUT_BLUESKY_USERNAME", None)
    BLUESKY_TOKEN = os.environ.get("INPUT_BLUESKY_TOKEN", None)


TWITTER_LINK_LENGTH = 24  # Includes an extra character for a '\n'
TWITTER_MAX_CHARS = 280
BLUESKY_MAX_CHARS = 300
POST_MAX_CHARS = min(TWITTER_MAX_CHARS, BLUESKY_MAX_CHARS)


def get_commit_list_entries(commit):
    """Extract an Awesome list entry from a given git commit in this repo."""
    diffs = commit.parents[0].diff(commit, create_patch=True)
    diff = diffs[0]

    # Check the git diff is what we expect
    exc_msg = "Can only analyse a single diff"
    if len(diffs) != 1:
        raise Exception(exc_msg + ".")
    if diff.a_path != diff.b_path != "README.md":
        raise Exception(exc_msg + " for the README.md file.")

    diff_change = diff.diff.decode("utf-8")
    diff_lines = diff_change.splitlines()
    entries = []
    for line in diff_lines:
        if line.startswith("+"):
            for match in re.finditer(
                r"-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.*)", line
            ):
                title, url, description = match.groups()
                entries.append(
                    {
                        "entry": line[1:],
                        "title": title,
                        "url": url,
                        "description": description,
                    }
                )

    if len(entries) == 0:
        raise Exception("Could not match an Awesome List entry.")
    return entries


def get_commit_readme(commit):
    """Return the README.md file contents at the given commit."""
    readme_file_blob = commit.tree / "README.md"
    with io.BytesIO(readme_file_blob.data_stream.read()) as f:
        readme_file = f.read().decode("utf-8")
    return readme_file


def get_entry_section(readme_str, list_entry):
    """Return the section an entry from the Awesome list belong to."""
    readme_lines = readme_str.splitlines()
    for line_number, line in enumerate(readme_lines):
        if line == list_entry:
            # Found the entry, now iterate backwards until we find a section
            for line in readme_lines[line_number::-1]:
                if line.startswith("#"):
                    return line.replace("#", "").strip()
    else:
        raise Exception("Could not find a section for the Awesome List entry.")


def format_use_hashtags(description):
    """Replace keywords in the content with hashtags."""
    description = description.replace(" microbit", " #microbit")
    description = description.replace(" micro:bit", " #microbit")
    description = description.replace(" Python", " #Python")
    description = description.replace(" python", " #Python")
    description = description.replace("MicroPython", "#MicroPython")
    description = description.replace("Micropython", "#MicroPython")
    description = description.replace("micropython", "#MicroPython")
    description = description.replace("Scratch", "#Scratch")
    description = description.replace("scratch", "#Scratch")
    description = description.replace("Raspberry Pi", "#RaspberryPi")
    description = description.replace("raspberry pi", "#RaspberryPi")
    description = description.replace("Raspberry pi", "#RaspberryPi")
    description = description.replace("raspberry Pi", "#RaspberryPi")
    description = description.replace("Arduino", "#Arduino")
    description = description.replace("arduino", "#Arduino")
    description = description.replace("MakeCode", "#MakeCode")
    description = description.replace("makecode", "#MakeCode")
    description = description.replace("Makecode", "#MakeCode")
    return description


def build_text_with_tags(text_builder, text):
    """Build text with proper hashtag tags for Bluesky.

    Parse text for hashtags (words starting with #) and use TextBuilder.tag()
    for hashtags and TextBuilder.text() for regular text.
    """
    # Pattern to match hashtags: # followed by alphanumeric characters
    # Split text by hashtags while keeping the delimiter
    parts = re.split(r"(#\w+)", text)

    for part in parts:
        if part.startswith("#") and len(part) > 1:
            # This is a hashtag - use tag() method
            # tag() takes display text (with #) and tag value (without #)
            text_builder.tag(part, part[1:])
        elif part:  # Skip empty strings
            # Regular text
            text_builder.text(part)

    return text_builder


def format_msg_twitter(section, title, url, description):
    """Format a tweet combining the title, description and URL.

    It ensures the total size does not exceed the tweet max characters limit.
    And it also replaces common words in the description to use hashtags.
    """
    # First let's introduce hashtags to the description
    description = format_use_hashtags(description)

    # Now let's make sure we don't exceed the 280 character limit
    max_characters = TWITTER_MAX_CHARS
    link_length = TWITTER_LINK_LENGTH
    msg = "{} - {}\n\n{}".format(section, title, description)
    if len(msg) > (max_characters - link_length):
        ellipsis = "..."
        cut_msg_len = max_characters - link_length - len(ellipsis)
        msg = msg[:cut_msg_len].rsplit(" ", 1)[0] + ellipsis
    return "{}\n{}".format(msg, url)


def tweet_msg(msg, dry_run=False):
    """Tweet the given message content."""
    if dry_run:
        print("Dry run: skipping Tweet.\n")
        return
    if not all(
        (
            TWITTER_CONSUMER_KEY,
            TWITTER_CONSUMER_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET,
        )
    ):
        print("Twitter access or consumer keys not available.")
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=TWITTER_CONSUMER_KEY,
        consumer_secret=TWITTER_CONSUMER_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    )
    client.create_tweet(text=msg)


def format_msg_bluesky(section, title, url, description):
    """Format a skeet combining the title, description and URL.

    It ensures the total size does not exceed the tweet max characters limit.
    And it also replaces common words in the description to use hashtags.
    """
    # First let's introduce hashtags to the description
    description = format_use_hashtags(description)

    # Now let's make sure we don't exceed the max character limit
    msg = "{} - {}\n\n{}".format(section, title, description)
    if len(msg) > BLUESKY_MAX_CHARS:
        ellipsis = "..."
        characters_over = len(msg) - BLUESKY_MAX_CHARS + len(ellipsis)
        description = (
            description[:-characters_over].rsplit(" ", 1)[0] + ellipsis
        )

    text_builder = client_utils.TextBuilder()
    text_builder.text(section + " - ")
    text_builder.link(title, url)
    text_builder.text("\n\n")
    build_text_with_tags(text_builder, description)
    return text_builder


def _get_og_tags(url):
    """Fetch OGP tags from a URL, download og:image.

    :param url: URL to fetch OGP tags from.
    :return: A tuple containing:
        - img_data: The og:image binary data, or None.
        - img_content_type: The og:image content type,
          or None.
        - og_image: The og:image URL, or None.
        - og_title: The og:title content, or None.
        - og_description: The og:description content,
          or None.
    """
    # Posting Open Graph Protocol (OGP) social media cards, based on example:
    # https://github.com/MarshalX/atproto/blob/v0.0.56/examples/advanced_usage/send_ogp_link_card.py
    _META_PATTERN = re.compile(r'<meta property="og:.*?>')
    _CONTENT_PATTERN = re.compile(r'<meta[^>]+content="([^"]+)"')

    def _get_og_tag_value(og_tags, tag_name):
        for tag in og_tags:
            if f'property="{tag_name}"' in tag:
                match = _CONTENT_PATTERN.match(tag)
                if match:
                    return match.group(1)
        return None

    def _detect_image_content_type(img_data, response_content_type):
        """Detect image content type from response header or magic bytes."""
        content_type = response_content_type.split(";")[0].strip()
        if not content_type.startswith("image/"):
            # Detect from magic bytes if header is missing/wrong
            if img_data[:8].startswith(b"\x89PNG\r\n\x1a\n"):
                content_type = "image/png"
            elif img_data[:2] in (b"\xff\xd8",):
                content_type = "image/jpeg"
            elif img_data[:4] == b"RIFF" and img_data[8:12] == b"WEBP":
                content_type = "image/webp"
            elif img_data[:6] in (b"GIF87a", b"GIF89a"):
                content_type = "image/gif"
            else:
                content_type = "image/jpeg"
        return content_type

    try:
        response = httpx.get(url)
        response.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"Warning: Could not fetch URL: {e}")
        return None, None, None, None, None
    og_tags = _META_PATTERN.findall(response.text)
    og_image = _get_og_tag_value(og_tags, "og:image")
    og_title = _get_og_tag_value(og_tags, "og:title")
    og_description = _get_og_tag_value(og_tags, "og:description")

    # Resolve relative image URLs to absolute URLs
    if og_image and not og_image.startswith(("http://", "https://")):
        og_image = urljoin(url, og_image)

    # Download the og:image and detect its content type
    img_data = None
    img_content_type = None
    if og_image:
        try:
            img_resp = httpx.get(og_image, follow_redirects=True)
            img_resp.raise_for_status()
            img_data = img_resp.content
            img_content_type = _detect_image_content_type(
                img_data, img_resp.headers.get("content-type", "")
            )
        except (httpx.HTTPStatusError, httpx.RequestError):
            print(f"Warning: og:image URL not accessible: {og_image}")
    return img_data, img_content_type, og_image, og_title, og_description


def skeet_msg(text_builder, url, dry_run=False):
    """Post to BlueSky the given message content."""
    # Always fetch OG content, even in dry run
    img_data, img_content_type, img_url, title, description = _get_og_tags(url)

    if dry_run:
        print("Dry run: skipping BlueSky post.")
        if title and description:
            print(
                f"BlueSky Embed content:\n\tTitle: {title}\n\tDescription: "
                f"{description}\n\tURL: {url}\n\tImage URL: {img_url}"
                f"\n\tImage type: {img_content_type or 'None'}"
            )
        return

    if not all((BLUESKY_USERNAME, BLUESKY_TOKEN)):
        print("BlueSky username or token not available.")
        sys.exit(1)
    client = Client()
    client.login(BLUESKY_USERNAME, BLUESKY_TOKEN)

    if title and description:
        thumb_blob = None
        if img_data:
            # Override Content-Type header (default is */* from the lexicon)
            # as BlueSky now requires image/* for blob uploads
            thumb_blob = client.com.atproto.repo.upload_blob(
                img_data, headers={"Content-Type": img_content_type}
            ).blob

        # AppBskyEmbedExternal is the same as "link card" in the app
        embed_external = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                title=title, description=description, uri=url, thumb=thumb_blob
            )
        )
        client.send_post(text=text_builder, embed=embed_external)
    else:
        client.send_post(text_builder)


def parse_cli_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Post new Awesome List entries to Twitter and BlueSky."
    )
    parser.add_argument(
        "--commit-hash",
        required=True,
        help="The git commit hash to process.",
    )
    parser.add_argument(
        "--trigger-keyword",
        required=True,
        help="Keyword to look for in the commit message.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print the messages without posting to Twitter or BlueSky.",
    )
    return parser.parse_args()


def main():
    """Entry point."""
    args = parse_cli_args()
    commit_hash = args.commit_hash
    post_trigger_str = args.trigger_keyword
    dry_run = args.dry_run
    print(f"Commit: {commit_hash}\nTrigger: {post_trigger_str}")
    if dry_run:
        print("Dry run mode enabled, will not post.")

    repo = Repo(os.getcwd())
    commit = repo.commit(commit_hash)
    print(f"Commit message:\n{commit.message}")
    if post_trigger_str not in commit.message:
        print("\n🤷 Tweet/Skeet trigger keyword not found, exiting...")
        sys.exit(0)

    print(f"\n{'-' * 50}\n🚀 Post trigger detected!\n{'-' * 50}\n")
    entries = get_commit_list_entries(commit)
    readme = get_commit_readme(commit)
    for i, entry in enumerate(entries):
        section = get_entry_section(readme, entry["entry"])
        formatted_tweet = format_msg_twitter(
            section, entry["title"], entry["url"], entry["description"]
        )
        formatted_skeet = format_msg_bluesky(
            section, entry["title"], entry["url"], entry["description"]
        )
        print(
            'Tweet msg #{}:\n\t"{}"'.format(
                i, formatted_tweet.replace("\n", "\n\t")
            )
            + '\n\nSkeet msg #{}:\n\t"{}"'.format(
                i, formatted_skeet.build_text().replace("\n", "\n\t")
            ),
            flush=True,
        )
        print(f"\n{'-' * 50}\nPosting #{i} to Social Media...\n{'-' * 50}\n")
        tweet_msg(formatted_tweet, dry_run=dry_run)
        skeet_msg(formatted_skeet, entry["url"], dry_run=dry_run)
        if not dry_run:
            print("✅ Sent Tweet and Skeet #{}!".format(i))


if __name__ == "__main__":
    main()
