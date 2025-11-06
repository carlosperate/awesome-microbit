"""GH Action entry point to post new entries to the Awesome micro:bit list.

It will post the same content to Twitter and BlueSky.

This script depends on environmental variables set by GitHub for the action,
including secrets set in the Awesome micro:bit repository for the Twitter
and BlueSky API access tokens.
It also depends on running with the Current Working Directory set to the
repository root.
"""

import os
import io
import re
import sys

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
    TWITTER_CONSUMER_SECRET = os.environ.get("INPUT_TWITTER_CONSUMER_SECRET", None)
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
            for match in re.finditer(r"-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.*)", line):
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
    msg = "{} - {}\n{}".format(section, title, description)
    if len(msg) > (max_characters - link_length):
        ellipsis = "..."
        cut_msg_len = max_characters - link_length - len(ellipsis)
        msg = msg[:cut_msg_len].rsplit(" ", 1)[0] + ellipsis
    return "{}\n{}".format(msg, url)


def tweet_msg(msg):
    """Tweet the given message content."""
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


def build_text_with_tags(text_builder, text):
    """Build text with proper hashtag tags for Bluesky.

    Parse text for hashtags (words starting with #) and use TextBuilder.tag()
    for hashtags and TextBuilder.text() for regular text.
    """
    # Pattern to match hashtags: # followed by alphanumeric characters
    # Note: Uses \w+ which matches ASCII alphanumeric and underscore.
    # This is sufficient for our use case as format_use_hashtags() only
    # creates hashtags from ASCII keywords (MakeCode, Python, etc.)
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
        description = description[:-characters_over].rsplit(" ", 1)[0] + ellipsis

    text_builder = client_utils.TextBuilder()
    text_builder.text(section + " - ")
    text_builder.link(title, url)
    text_builder.text("\n\n")
    build_text_with_tags(text_builder, description)
    return text_builder


def skeet_msg(text_builder, url):
    """Post to BluSky the given message content."""
    if not all((BLUESKY_USERNAME, BLUESKY_TOKEN)):
        print("BlueSky username or token not available.")
        sys.exit(1)

    # Posting Open Graph Protocol (OGP) social media cards, based on example:
    # https://github.com/MarshalX/atproto/blob/v0.0.56/examples/advanced_usage/send_ogp_link_card.py
    _META_PATTERN = re.compile(r'<meta property="og:.*?>')
    _CONTENT_PATTERN = re.compile(r'<meta[^>]+content="([^"]+)"')

    def _get_og_tag_value(og_tags, tag_name):
        # tag = _find_tag(og_tags, tag_name)
        for tag in og_tags:
            if tag_name in tag:
                match = _CONTENT_PATTERN.match(tag)
                if match:
                    return match.group(1)
        return None

    def _get_og_tags(url):
        response = httpx.get(url)
        response.raise_for_status()
        og_tags = _META_PATTERN.findall(response.text)
        og_image = _get_og_tag_value(og_tags, "og:image")
        og_title = _get_og_tag_value(og_tags, "og:title")
        og_description = _get_og_tag_value(og_tags, "og:description")
        return og_image, og_title, og_description

    client = Client()
    client.login(BLUESKY_USERNAME, BLUESKY_TOKEN)

    # Process social media card
    img_url, title, description = _get_og_tags(url)
    if title and description:
        thumb_blob = None
        if img_url:
            # Download image from og:image url and upload it as a blob
            img_data = httpx.get(img_url).content
            thumb_blob = client.upload_blob(img_data).blob

        # AppBskyEmbedExternal is the same as "link card" in the app
        embed_external = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                title=title, description=description, uri=url, thumb=thumb_blob
            )
        )
        client.send_post(text=text_builder, embed=embed_external)
    else:
        client.send_post(text_builder)


def main():
    """Entry point."""
    commit_hash = os.environ["GITHUB_SHA"]
    post_trigger_str = os.environ["INPUT_TRIGGER_KEYWORD"]
    print("Commit: {}\nTrigger: {}".format(commit_hash, post_trigger_str))

    repo = Repo(os.getcwd())
    commit = repo.commit(commit_hash)
    if post_trigger_str not in commit.message:
        print("Tweet/Skeet trigger keyword not found, exiting...")
        sys.exit(0)

    print("Post trigger detected, let's tweet and skeet!")
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
            'Tweet msg #{}:\n\t"{}"'.format(i, formatted_tweet.replace("\n", "\n\t"))
            + '\nSkeet msg #{}:\n\t"{}"'.format(
                i, formatted_skeet.build_text().replace("\n", "\n\t")
            ),
            flush=True,
        )
        tweet_msg(formatted_tweet)
        skeet_msg(formatted_skeet, entry["url"])
        print("Sent Tweet and Skeet #{}!".format(i))


if __name__ == "__main__":
    main()
