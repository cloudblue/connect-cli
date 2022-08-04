import subprocess

from connect.cli import get_version
from connect.cli.core.utils import sort_and_filter_tags


class GitException(Exception):
    pass


def _list_tags(repo_url):
    result = subprocess.run(
        ['git', 'ls-remote', '--tags', '--refs', repo_url],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise GitException(result.stderr.decode())

    tags = {}
    for line in result.stdout.decode().splitlines():
        commit, tagref = line.split()
        tag = tagref.rsplit('/', 1)[-1]
        tags[tag] = commit

    return tags


def get_highest_version(repo_url):
    tags = _list_tags(repo_url)
    desired_major, _ = get_version().split('.', 1)
    tags = sort_and_filter_tags(tags, desired_major)
    return tags.popitem() if tags else (None, None)
