#!/bin/bash
set -e

# Required in CI, otherwise it errors with:
#
# fatal: detected dubious ownership in repository at '/github/workspace'
# To add an exception for this directory, call:
#
#    git config --global --add safe.directory /github/workspace
git config --global --add safe.directory /github/workspace

if [[ "$1" == "test" ]]; then
    echo "Running the tests:"
    python .github/actions/tweet-commit/tests.py
    echo "Running flake8:"
    flake8 .github/actions/tweet-commit/post_commit.py .github/actions/tweet-commit/tests.py
    echo "Running black:"
    black .github/actions/tweet-commit/post_commit.py .github/actions/tweet-commit/tests.py --check --diff --line-length 79
else
    echo "Tweeting new Awesome List entry:"
    python .github/actions/tweet-commit/post_commit.py
fi
