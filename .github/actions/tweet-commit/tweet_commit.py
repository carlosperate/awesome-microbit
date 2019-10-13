import os
import re
import sys

from git import Repo
import tweepy

# Getting the Twitter secrets form local dev file or GH action secrets
try:
    from twitter_secrets import *
except ImportError:
    TWITTER_API_KEY = os.environ.get('INPUT_TWITTER_API_KEY', None)
    TWITTER_API_SECRET_KEY = os.environ.get('INPUT_TWITTER_API_SECRET_KEY', None)
    TWITTER_ACCESS_TOKEN = os.environ.get('INPUT_TWITTER_ACCESS_TOKEN', None)
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('INPUT_TWITTER_ACCESS_TOKEN_SECRET', None)


def get_commit_msg(commit_hash):
    repository_path = os.getcwd()
    repo = Repo(repository_path)
    commit = repo.commit(commit_hash)
    return commit.message


def get_commit_list_entries(commit_hash):
    """Extracts an Awesome list entry from a given git commit in this repo."""
    repository_path = os.getcwd()
    repo = Repo(repository_path)
    commit = repo.commit(commit_hash)
    diffs = commit.parents[0].diff(commit, create_patch=True)
    diff = diffs[0]

    # Check the git diff is what we expect
    exc_msg = 'Can only analyse a single diff'
    if len(diffs) != 1:
        raise Exception(exc_msg + '.')
    if diff.a_path != diff.b_path != 'README.md':
        raise Exception(exc_msg + ' for the README.md file.')

    diff_change = diff.diff.decode('utf-8')
    diff_lines = diff_change.splitlines()
    entries = []
    for line in diff_lines:
        if line.startswith('+'):
            for match in re.finditer("-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.*)", line):
                # end_char  = match.span()[1] + 1 # Want to be off by one to bypass stop
                title, url, description = match.groups()
                entries.append({
                    "title": title,
                    "url": url,
                    "description": description
                })

    if len(entries) == 0:
        raise Exception('Could not match an Awesome List entry.')
    return entries


def format_tweet_msg(title, url, description):
    """Formats a tweet combining the title, description and URL.

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
    # Now let's make sure we don't exceed the 280 character limit
    max_characters = 280
    link_length = 24    # Includes an extra character for a '\n'
    msg = "{} - {}".format(title, description)
    if len(msg) > (max_characters - link_length):
        ellipsis = "..."
        cut_msg_len = max_characters - link_length - len(ellipsis)
        msg = msg[:cut_msg_len].rsplit(" ", 1)[0] + ellipsis
    return "{}\n{}".format(msg, url)


def tweet_msg(msg):
    """Tweets the given message content."""
    # Authenticate to Twitter and create API object
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    tw = tweepy.API(auth)
    tw.verify_credentials()
    tw.update_status(msg)


def main():
    commit_hash = os.environ['GITHUB_SHA']
    tweet_trigger_str = os.environ['INPUT_TRIGGER_KEYWORD']
    print('Commit: {}\nTrigger: {}'.format(commit_hash, tweet_trigger_str))
    commit_msg = get_commit_msg(commit_hash)
    if tweet_trigger_str not in commit_msg:
        print('Tweet trigger keyword not found, exiting...')
        sys.exit(0)

    print('Tweet trigger detected, let\'s tweet!')
    entries = get_commit_list_entries(commit_hash)
    for i, entry in enumerate(entries):
        msg = format_tweet_msg(entry["title"], entry["url"], entry["description"])
        print("Tweet msg #{}:\n\t\"{}\"".format(i, msg.replace("\n", "\n\t")))
        tweet_msg(msg)
        print('Tweeted #{}!'.format(i))


if __name__ == "__main__":
    main()
