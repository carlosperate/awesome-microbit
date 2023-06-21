"""GH Action entry point to tweet new entries to the Awesome micro:bit list.

This script depends on environmental variables set by GitHub for the action,
including secrets set in the Awesome micro:bit repository for the Twitter
tokens.
It also depends on running with the Current Working Directory set to the
repository root.
"""
import os
import io
import re
import sys

from git import Repo
import tweepy

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


def format_tweet_msg(section, title, url, description):
    """Format a tweet combining the title, description and URL.

    It ensures the total size does not exceed the tweet max characters limit.
    And it also replaces common words in the description to use hashtags.
    """
    # First let's introduce hashtags to the description
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
    # Now let's make sure we don't exceed the 280 character limit
    max_characters = 280
    link_length = 24  # Includes an extra character for a '\n'
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


def main():
    """Entry point."""
    commit_hash = os.environ["GITHUB_SHA"]
    tweet_trigger_str = os.environ["INPUT_TRIGGER_KEYWORD"]
    print("Commit: {}\nTrigger: {}".format(commit_hash, tweet_trigger_str))

    repo = Repo(os.getcwd())
    commit = repo.commit(commit_hash)
    if tweet_trigger_str not in commit.message:
        print("Tweet trigger keyword not found, exiting...")
        sys.exit(0)

    print("Tweet trigger detected, let's tweet!")
    entries = get_commit_list_entries(commit)
    readme = get_commit_readme(commit)
    for i, entry in enumerate(entries):
        section = get_entry_section(readme, entry["entry"])
        msg = format_tweet_msg(
            section, entry["title"], entry["url"], entry["description"]
        )
        print(
            'Tweet msg #{}:\n\t"{}"'.format(i, msg.replace("\n", "\n\t")),
            flush=True,
        )
        tweet_msg(msg)
        print("Tweeted #{}!".format(i))


if __name__ == "__main__":
    main()
