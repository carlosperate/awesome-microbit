#!/bin/bash
if [[ "$1" == "test" ]]; then
    echo "Running the tests:"
    sh -c "python .github/actions/tweet-commit/tests.py"
else
    echo "Tweeting new Awesome List entry:"
    sh -c "python .github/actions/tweet-commit/tweet_commit.py"
fi
