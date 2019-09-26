import os
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


def get_commit_msg():
    repository_path = os.getcwd()
    trigger_commit_sha = os.environ['GITHUB_SHA']

    # Get the commit message that triggered this action
    repo = Repo(repository_path)
    return repo.commit(trigger_commit_sha).message


def tweet_msg(msg):
    # Authenticate to Twitter and create API object
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    tw = tweepy.API(auth)
    tw.verify_credentials()

    # Create a tweet
    tw.update_status(msg)


def main():
    commit_msg = get_commit_msg()
    tweet_trigge_str = os.environ['INPUT_TRIGGER_KEYWORD']
    if tweet_trigge_str not in commit_msg:
        print('Tweet trigger keyword not found, exiting...')
        sys.exit(0)

    print('Tweet trigger detected, let\'s tweet!')
    tweet_msg('First tweet from a GitHub action!')


if __name__ == "__main__":
    main()
