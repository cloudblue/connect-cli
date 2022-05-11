import os
import re
import shutil
import stat
from collections import OrderedDict
from distutils.version import StrictVersion


def force_delete(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def purge_dir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir, onerror=force_delete)


def slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')


class _ConnectVersionTag(StrictVersion):

    version_re = re.compile(
        r'^v?(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
        re.VERBOSE | re.ASCII,
    )

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
            other = _ConnectVersionTag(other)
        elif not isinstance(other, _ConnectVersionTag):
            return NotImplemented

        result = self._cmp_plain_tag(self.plain_tag, other.plain_tag)
        if result is not None:
            return result

        return super()._cmp(other)


def sort_and_filter_tags(tags, desired_major):
    sorted_tags = OrderedDict()
    for tag in sorted(tags.keys(), key=_ConnectVersionTag):
        match = _ConnectVersionTag.version_re.match(tag)
        if not match:
            continue
        major = match.group(1)
        if major != desired_major:
            continue
        sorted_tags[tag] = tags[tag]

    return sorted_tags
