import os

from git import Repo

print('Hello world!')

repo = Repo(os.getcwd())
msg = repo.commit('master').message

print('Last commit message:\n"{}"'.format(msg))
