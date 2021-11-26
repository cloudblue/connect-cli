import re
import subprocess
from distutils.version import StrictVersion
from collections import OrderedDict

from connect.cli import get_version


class GitException(Exception):
    pass


class ConnectVersionTag(StrictVersion):

    version_re = re.compile(r'^v?(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                            re.VERBOSE | re.ASCII)

    plain_tag = None

    def parse(self, vstring):
        try:
            super().parse(vstring)
        except Exception:
            print('Exception ', vstring)
            self.plain_tag = vstring

    def _cmp_plain_tag(self, actual, other):
        if actual and other:
            if actual == other:
                return 0
            return -1 if actual < other else 1
        elif not actual and other:
            return 1
        if actual and not other:
            return -1
        return None

    def _cmp(self, other):
        if isinstance(other, str):
            other = ConnectVersionTag(other)
        elif not isinstance(other, ConnectVersionTag):
            return NotImplemented

        result = self._cmp_plain_tag(self.plain_tag, other.plain_tag)
        if result is not None:
            return result

        return super()._cmp(other)


def _sort_and_filter_tags(tags, desired_major):
    sorted_tags = OrderedDict()
    for tag in sorted(tags.keys(), key=ConnectVersionTag):
        match = ConnectVersionTag.version_re.match(tag)
        if not match:
            continue
        major = match.group(1)
        if major != desired_major:
            continue
        sorted_tags[tag] = tags[tag]

    return sorted_tags


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
    tags = _sort_and_filter_tags(tags, desired_major)
    return tags.popitem() if tags else (None, None)
