import os
import re
import sys

from git import Repo
import tweepy

# Getting the Twitter secrets form local dev file or GH action secrets
try:
    from twitter_secrets import *
except ImportError:
    TWITTER_API_KEY = os.environ['INPUT_TWITTER_API_KEY']
    TWITTER_API_SECRET_KEY = os.environ['INPUT_TWITTER_API_SECRET_KEY']
    TWITTER_ACCESS_TOKEN = os.environ['INPUT_TWITTER_ACCESS_TOKEN']
    TWITTER_ACCESS_TOKEN_SECRET = os.environ['INPUT_TWITTER_ACCESS_TOKEN_SECRET']


project_root_dir = \
    os.path.dirname(os.path.dirname(os.path.dirname(    # Going up 3 levels
        os.path.dirname(os.path.realpath(__file__)))))  # This file folder dir


def get_commit_info(commit_hash):
    repository_path = project_root_dir
    repo = Repo(repository_path)
    if not commit_hash:
        # Get the commit message that triggered this action
        commit_hash = os.environ['GITHUB_SHA']
    commit = repo.commit(commit_hash)
    commit_msg = commit.message
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
                return (commit_msg, title, url, description)
    return commit_msg, None, None, None


def format_tweet_msg(entry_title, entry_url, entry_description):
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
    tweet_trigge_str = os.environ['INPUT_TRIGGER_KEYWORD']
    commit_msg, entry_title, entry_url, entry_description = get_commit_info()
    if tweet_trigge_str not in commit_msg:
        print('Tweet trigger keyword not found, exiting...')
        sys.exit(0)

    print('Tweet trigger detected, let\'s tweet!')
    msg = format_tweet_msg(entry_title, entry_url, entry_description)
    if not entry_title:
        print('Could not match an awesome list entry.')
        sys.exit(1)
    print('Tweet msg:\n\t"{}"'.format(msg))
    tweet_msg(msg)
    print('Tweeted!')


if __name__ == "__main__":
    main()
