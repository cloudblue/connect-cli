from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = '0.0.0'


def get_version():
    return __version__