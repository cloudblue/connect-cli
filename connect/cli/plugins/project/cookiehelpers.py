import os
import shutil

from cookiecutter import generate
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.utils import rmtree


def purge_cookiecutters_dir():
    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    if os.path.isdir(cookie_dir):
        rmtree(cookie_dir)


def slugify(name):
    return name.lower().strip().replace(' ', '_').replace('-', '_').replace('.', '_').replace(',', '')


def remove_github_actions(project_dir: str):
    shutil.rmtree(f'{project_dir}/.github')


def monkey_patch():
    def _run_hook_from_repo_dir(
        repo_dir, hook_name, project_dir, context, delete_project_on_failure,
    ):  # pragma: no cover
        '''Fake method for monkey patching purposes'''
        pass
    generate._run_hook_from_repo_dir = _run_hook_from_repo_dir
