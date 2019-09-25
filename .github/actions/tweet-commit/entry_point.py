import os

from git import Repo

print('Hello world!')

repository_path = os.getcwd()
trigger_commit_sha = os.environ['GITHUB_SHA']
repo = Repo(repository_path)
msg = repo.commit(trigger_commit_sha).message

print('Trigger commit message:\n"{}"'.format(msg))
