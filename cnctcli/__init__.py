from setuptools_scm import get_version as scm_version

try:
    __version__ = scm_version(root='..', relative_to=__file__)
except:   # noqa: E722
    __version__ = '0.0.1'


def get_version():
    return __version__
