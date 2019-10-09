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


def get_commit_list_entry(commit_hash):
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
    for line in diff_lines:
        if line.startswith('+'):
            for match in re.finditer("-[ ]\[(.*?)\]\((.*?)\)[ ]-[ ](.*)", line):
                # end_char  = match.span()[1] + 1 # Want to be off by one to bypass stop
                title, url, description = match.groups()
                return title, url, description

    raise Exception('Could not match an awesome list entry.')


def format_tweet_msg(entry_title, entry_url, entry_description):
    """Formats a tweet combining the title, description and URL.

    It also replaces common words in the description to use hashtags.
    """
    entry_description = entry_description.replace(" microbit", " #microbit")
    entry_description = entry_description.replace(" micro:bit", " #microbit")
    entry_description = entry_description.replace(" Python", " #Python")
    entry_description = entry_description.replace(" python", " #Python")
    entry_description = entry_description.replace("MicroPython", "#MicroPython")
    entry_description = entry_description.replace("Micropython", "#MicroPython")
    entry_description = entry_description.replace("micropython", "#MicroPython")
    msg = "{}: {}\n{}".format(entry_title, entry_description, entry_url)
    return msg


def tweet_msg(msg):
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
    entry_title, entry_url, entry_description = get_commit_list_entry(commit_hash)
    msg = format_tweet_msg(entry_title, entry_url, entry_description)
    print('Tweet msg:\n\t"{}"'.format(msg))
    tweet_msg(msg)
    print('Tweeted!')


if __name__ == "__main__":
    main()
