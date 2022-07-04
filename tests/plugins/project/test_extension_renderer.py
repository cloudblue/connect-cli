import os
import tempfile

import pytest
from click import ClickException

from connect.cli.plugins.project.extension.renderer import BoilerplateRenderer
from connect.cli.plugins.project.utils import slugify


def test_render(faker):
    ctx = {
        'statuses_by_event': {'sample_background_event': ['status1']},
        'background': {
            'background_group': ['sample_background_event'],
        },
        'interactive': {},
        'runner_version': '25.5',
        'project_name': faker.name(),
        'project_slug': slugify(faker.name()),
        'description': 'desc',
        'package_name': slugify(faker.name()),
        'author': 'connect',
        'version': '1.0',
        'license': 'Apache',
        'use_github_actions': 'y',
        'use_asyncio': 'y',
        'include_schedules_example': 'y',
        'include_variables_example': 'y',
        'api_key': faker.pystr(),
        'environment_id': f'ENV-{faker.random_number()}',
        'server_address': faker.domain_name(2),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        renderer = BoilerplateRenderer(tmpdir, ctx, False)
        renderer.render()

        assert os.path.isdir(os.path.join(tmpdir, ctx['project_slug']))


def test_render_destination_exists(faker):
    ctx = {
        'statuses_by_event': {'sample_background_event': ['status1']},
        'background': {
            'background_group': ['sample_background_event'],
        },
        'interactive': {},
        'runner_version': '25.5',
        'project_name': faker.name(),
        'project_slug': 'existing_folder',
        'description': 'desc',
        'package_name': slugify(faker.name()),
        'author': 'connect',
        'version': '1.0',
        'license': 'Apache',
        'use_github_actions': 'y',
        'use_asyncio': 'y',
        'include_schedules_example': 'y',
        'include_variables_example': 'y',
        'api_key': faker.pystr(),
        'environment_id': f'ENV-{faker.random_number()}',
        'server_address': faker.domain_name(2),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        dst_dir = os.path.join(tmpdir, 'existing_folder')
        os.makedirs(dst_dir)
        renderer = BoilerplateRenderer(tmpdir, ctx, False)
        with pytest.raises(ClickException) as cv:
            renderer.render()

        assert str(cv.value) == f'The destination directory {dst_dir} already exists.'


def test_render_destination_exists_owerwrite(faker):
    ctx = {
        'statuses_by_event': {'sample_background_event': ['status1']},
        'background': {
            'background_group': ['sample_background_event'],
        },
        'interactive': {},
        'runner_version': '25.5',
        'project_name': faker.name(),
        'project_slug': 'existing_folder',
        'description': 'desc',
        'package_name': slugify(faker.name()),
        'author': 'connect',
        'version': '1.0',
        'license': 'Apache',
        'use_github_actions': 'y',
        'use_asyncio': 'y',
        'include_schedules_example': 'y',
        'include_variables_example': 'y',
        'api_key': faker.pystr(),
        'environment_id': f'ENV-{faker.random_number()}',
        'server_address': faker.domain_name(2),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        dst_dir = os.path.join(tmpdir, 'existing_folder')
        os.makedirs(dst_dir)
        renderer = BoilerplateRenderer(tmpdir, ctx, True)
        renderer.render()

        assert os.path.exists(os.path.join(tmpdir, ctx['project_slug'], 'pyproject.toml'))
