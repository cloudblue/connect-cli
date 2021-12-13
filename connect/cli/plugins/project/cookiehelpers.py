import os
import shutil
import stat

from cookiecutter.config import DEFAULT_CONFIG


def force_delete(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def purge_cookiecutters_dir():
    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    if os.path.isdir(cookie_dir):
        shutil.rmtree(cookie_dir, onerror=force_delete)


def slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')
