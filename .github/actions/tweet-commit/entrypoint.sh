#!/bin/bash
set -e

if [[ "$1" == "test" ]]; then
    echo "Running the tests:"
    python .github/actions/tweet-commit/tests.py
    echo "Running flake8:"
    flake8 .github/actions/tweet-commit/tweet_commit.py .github/actions/tweet-commit/tests.py
    echo "Running black:"
    black .github/actions/tweet-commit/tweet_commit.py .github/actions/tweet-commit/tests.py --check --diff --line-length 79
else
    echo "Tweeting new Awesome List entry:"
    python .github/actions/tweet-commit/tweet_commit.py
fi
