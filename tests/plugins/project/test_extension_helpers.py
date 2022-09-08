#  Copyright © 2022 CloudBlue. All rights reserved.

import configparser
import os
import tempfile

import pytest
import toml
import yaml
from click import ClickException
from flake8.api import legacy as flake8

from connect.cli.plugins.project.extension.helpers import (
    bootstrap_extension_project,
    bump_runner_extension_project,
    validate_extension_project,
)
from connect.cli.plugins.project.utils import slugify


@pytest.mark.parametrize('async_impl', (True, False))
@pytest.mark.parametrize('with_variables', (True, False))
@pytest.mark.parametrize('with_schedulable', (True, False))
@pytest.mark.parametrize('with_github_actions', (True, False))
def test_bootstrap_extension_project_background(
    faker,
    mocker,
    mocked_responses,
    config_vendor,
    extension_class_declaration,
    extension_imports,
    extension_bg_event,
    extension_schedulable_event,
    test_bg_event,
    test_schedulable_event,
    async_impl,
    with_variables,
    with_schedulable,
    with_github_actions,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        runner_version = f'{faker.random_number()}.{faker.random_number()}'
        mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
            return_value=runner_version,
        )
        config_vendor.load(config_dir='/tmp')

        mocked_responses.add(
            method='GET',
            url=f'{config_vendor.active.endpoint}/devops/event-definitions',
            headers={
                'Content-Range': 'items 0-0/1',
            },
            json=[
                {
                    'type': 'sample_background_event',
                    'group': 'Group',
                    'name': 'Sample Event',
                    'extension_type': 'products',
                    'category': 'background',
                    'object_statuses': ['status1', 'status2'],
                },
            ],
        )

        data = {
            'project_name': faker.name(),
            'project_slug': slugify(faker.name()),
            'extension_type': 'products',
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'y' if with_github_actions else 'n',
            'use_asyncio': 'y' if async_impl else 'n',
            'include_schedules_example': 'y' if with_schedulable else 'n',
            'include_variables_example': 'y' if with_variables else 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'background': ['sample_background_event'],
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config=config_vendor, output_dir=tmpdir, overwrite=False)

        classname_prefix = data['project_slug'].replace('_', ' ').title().replace(' ', '')

        env_file_name = f".{data['project_slug']}_dev.env"

        env_file = open(os.path.join(tmpdir, data['project_slug'], env_file_name)).read()
        assert f'export API_KEY="{data["api_key"]}"' in env_file
        assert f'export ENVIRONMENT_ID="{data["environment_id"]}"' in env_file
        assert f'export SERVER_ADDRESS="{data["server_address"]}"' in env_file

        docker_compose_yml = yaml.safe_load(
            open(os.path.join(tmpdir, data['project_slug'], 'docker-compose.yml')),
        )

        for service_suffix in ('dev', 'bash', 'test'):
            service = docker_compose_yml['services'][f"{data['project_slug']}_{service_suffix}"]
            assert service['container_name'] == f"{data['project_slug']}_{service_suffix}"
            assert service['image'] == f'cloudblueconnect/connect-extension-runner:{runner_version}'
            assert service['env_file'] == [env_file_name]

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {'extension': f"{data['package_name']}.events:{classname_prefix}Extension"}

        if with_github_actions:
            assert os.path.exists(
                os.path.join(tmpdir, data['project_slug'], '.github', 'workflows', 'build.yml'),
            ) is True

        parser = configparser.ConfigParser()
        parser.read(os.path.join(tmpdir, data['project_slug'], '.flake8'))

        assert parser['flake8']['application-import-names'] == data['package_name']

        flake8_style_guide = flake8.get_style_guide(
            show_source=parser['flake8']['show-source'],
            max_line_length=int(parser['flake8']['max-line-length']),
            application_import_names=parser['flake8']['application-import-names'],
            import_order_style=parser['flake8']['import-order-style'],
            max_cognitive_complexity=parser['flake8']['max-cognitive-complexity'],
            ignore=parser['flake8']['ignore'],
            exclude=parser['flake8']['exclude'],
        )

        report = flake8_style_guide.check_files([
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ])
        assert report.total_errors == 0

        extension_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ).read()

        expected_imports = extension_imports(
            with_schedulable=with_schedulable,
            with_variables=with_variables,
        )

        assert expected_imports in extension_py
        assert extension_class_declaration(
            classname_prefix,
            with_variables=with_variables,
        ) in extension_py

        assert extension_bg_event(async_impl=async_impl) in extension_py

        test_py = open(
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ).read()

        assert test_bg_event(classname_prefix, async_impl=async_impl) in test_py

        if with_schedulable:
            assert extension_schedulable_event(async_impl=async_impl) in extension_py
            assert test_schedulable_event(classname_prefix, async_impl=async_impl) in test_py


@pytest.mark.parametrize('async_impl', (True, False))
@pytest.mark.parametrize('with_variables', (True, False))
@pytest.mark.parametrize('with_schedulable', (True, False))
@pytest.mark.parametrize('with_github_actions', (True, False))
def test_bootstrap_extension_project_interactive(
    faker,
    mocker,
    mocked_responses,
    config_vendor,
    extension_class_declaration,
    extension_imports,
    extension_interactive_event,
    extension_schedulable_event,
    test_interactive_event,
    test_schedulable_event,
    async_impl,
    with_variables,
    with_schedulable,
    with_github_actions,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        runner_version = f'{faker.random_number()}.{faker.random_number()}'
        mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
            return_value=runner_version,
        )
        config_vendor.load(config_dir='/tmp')

        mocked_responses.add(
            method='GET',
            url=f'{config_vendor.active.endpoint}/devops/event-definitions',
            headers={
                'Content-Range': 'items 0-0/1',
            },
            json=[
                {
                    'type': 'sample_interactive_event',
                    'group': 'Group',
                    'name': 'Sample Event',
                    'extension_type': 'products',
                    'category': 'interactive',
                    'object_statuses': ['status1', 'status2'],
                },
            ],
        )

        data = {
            'project_name': faker.name(),
            'project_slug': slugify(faker.name()),
            'extension_type': 'products',
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'y' if with_github_actions else 'n',
            'use_asyncio': 'y' if async_impl else 'n',
            'include_schedules_example': 'y' if with_schedulable else 'n',
            'include_variables_example': 'y' if with_variables else 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'interactive': ['sample_interactive_event'],
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config_vendor, tmpdir, False)

        env_file_name = f".{data['project_slug']}_dev.env"

        env_file = open(os.path.join(tmpdir, data['project_slug'], env_file_name)).read()
        assert f'export API_KEY="{data["api_key"]}"' in env_file
        assert f'export ENVIRONMENT_ID="{data["environment_id"]}"' in env_file
        assert f'export SERVER_ADDRESS="{data["server_address"]}"' in env_file

        docker_compose_yml = yaml.safe_load(
            open(os.path.join(tmpdir, data['project_slug'], 'docker-compose.yml')),
        )

        for service_suffix in ('dev', 'bash', 'test'):
            service = docker_compose_yml['services'][f"{data['project_slug']}_{service_suffix}"]
            assert service['container_name'] == f"{data['project_slug']}_{service_suffix}"
            assert service['image'] == f'cloudblueconnect/connect-extension-runner:{runner_version}'
            assert service['env_file'] == [env_file_name]

        classname_prefix = data['project_slug'].replace('_', ' ').title().replace(' ', '')

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {'extension': f"{data['package_name']}.events:{classname_prefix}Extension"}

        if with_github_actions:
            assert os.path.exists(
                os.path.join(tmpdir, data['project_slug'], '.github', 'workflows', 'build.yml'),
            ) is True

        parser = configparser.ConfigParser()
        parser.read(os.path.join(tmpdir, data['project_slug'], '.flake8'))

        assert parser['flake8']['application-import-names'] == data['package_name']

        flake8_style_guide = flake8.get_style_guide(
            show_source=parser['flake8']['show-source'],
            max_line_length=int(parser['flake8']['max-line-length']),
            application_import_names=parser['flake8']['application-import-names'],
            import_order_style=parser['flake8']['import-order-style'],
            max_cognitive_complexity=parser['flake8']['max-cognitive-complexity'],
            ignore=parser['flake8']['ignore'],
            exclude=parser['flake8']['exclude'],
        )

        report = flake8_style_guide.check_files([
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ])
        assert report.total_errors == 0

        extension_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ).read()

        expected_imports = extension_imports(
            with_schedulable=with_schedulable,
            with_variables=with_variables,
            with_background=False,
            with_interactive=True,
        )

        assert expected_imports in extension_py
        assert extension_class_declaration(classname_prefix, with_variables=with_variables) in extension_py

        assert extension_interactive_event(async_impl=async_impl) in extension_py

        test_py = open(
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ).read()

        assert test_interactive_event(classname_prefix, async_impl=async_impl) in test_py

        if with_schedulable:
            assert extension_schedulable_event(async_impl=async_impl) in extension_py
            assert test_schedulable_event(classname_prefix, async_impl=async_impl) in test_py


def test_bootstrap_extension_project_multiaccount(
    faker,
    mocker,
    mocked_responses,
    config_vendor,
    extension_bg_event,
    test_bg_event,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        runner_version = f'{faker.random_number()}.{faker.random_number()}'
        mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
            return_value=runner_version,
        )
        config_vendor.load(config_dir='/tmp')

        mocked_responses.add(
            method='GET',
            url=f'{config_vendor.active.endpoint}/devops/event-definitions',
            headers={
                'Content-Range': 'items 0-0/1',
            },
            json=[
                {
                    'type': 'sample_background_event',
                    'group': 'Group',
                    'name': 'Sample Event',
                    'extension_type': 'multiaccount',
                    'category': 'background',
                    'object_statuses': ['status1', 'status2'],
                },
            ],
        )

        data = {
            'project_name': faker.name(),
            'project_slug': slugify(faker.name()),
            'extension_type': 'multiaccount',
            'application_types': ['anvil', 'events'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
            'include_schedules_example': 'n',
            'include_variables_example': 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'background': ['sample_background_event'],
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config=config_vendor, output_dir=tmpdir, overwrite=False)

        classname_prefix = data['project_slug'].replace('_', ' ').title().replace(' ', '')

        env_file_name = f".{data['project_slug']}_dev.env"

        env_file = open(os.path.join(tmpdir, data['project_slug'], env_file_name)).read()
        assert f'export API_KEY="{data["api_key"]}"' in env_file
        assert f'export ENVIRONMENT_ID="{data["environment_id"]}"' in env_file
        assert f'export SERVER_ADDRESS="{data["server_address"]}"' in env_file

        docker_compose_yml = yaml.safe_load(
            open(os.path.join(tmpdir, data['project_slug'], 'docker-compose.yml')),
        )

        for service_suffix in ('dev', 'bash', 'test'):
            service = docker_compose_yml['services'][f"{data['project_slug']}_{service_suffix}"]
            assert service['container_name'] == f"{data['project_slug']}_{service_suffix}"
            assert service['image'] == f'cloudblueconnect/connect-extension-runner:{runner_version}'
            assert service['env_file'] == [env_file_name]

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'anvil': f"{data['package_name']}.anvil:{classname_prefix}AnvilExtension",
            'extension': f"{data['package_name']}.events:{classname_prefix}Extension",
        }

        parser = configparser.ConfigParser()
        parser.read(os.path.join(tmpdir, data['project_slug'], '.flake8'))

        assert parser['flake8']['application-import-names'] == data['package_name']

        flake8_style_guide = flake8.get_style_guide(
            show_source=parser['flake8']['show-source'],
            max_line_length=int(parser['flake8']['max-line-length']),
            application_import_names=parser['flake8']['application-import-names'],
            import_order_style=parser['flake8']['import-order-style'],
            max_cognitive_complexity=parser['flake8']['max-cognitive-complexity'],
            ignore=parser['flake8']['ignore'],
            exclude=parser['flake8']['exclude'],
        )

        report = flake8_style_guide.check_files([
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ])
        assert report.total_errors == 0

        events_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ).read()
        anvil_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'anvil.py'),
        ).read()

        assert 'from connect.eaas.core.extension import EventsExtension' in events_py
        assert f'class {classname_prefix}Extension(BaseExtension):' in events_py
        assert f'class {classname_prefix}AnvilExtension(AnvilExtension):' in anvil_py

        assert extension_bg_event(async_impl=False) in events_py

        test_py = open(
            os.path.join(tmpdir, data['project_slug'], 'tests', f'test_{data["project_slug"]}.py'),
        ).read()

        assert test_bg_event(classname_prefix, async_impl=False) in test_py

        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'webapp.py'),
        ) is False
        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ) is True


def test_bootstrap_extension_project_webapp(
    faker,
    mocker,
    mocked_responses,
    config_provider,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        runner_version = f'{faker.random_number()}.{faker.random_number()}'
        mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
            return_value=runner_version,
        )
        config_provider.load(config_dir='/tmp')

        mocked_responses.add(
            method='GET',
            url=f'{config_provider.active.endpoint}/devops/event-definitions',
            headers={
                'Content-Range': 'items 0-0/1',
            },
            json=[
                {
                    'type': 'sample_background_event',
                    'group': 'Group',
                    'name': 'Sample Event',
                    'extension_type': 'multiaccount',
                    'category': 'background',
                    'object_statuses': ['status1', 'status2'],
                },
            ],
        )

        data = {
            'project_name': faker.name(),
            'project_slug': slugify(faker.name()),
            'extension_type': 'multiaccount',
            'application_types': ['webapp'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
            'include_schedules_example': 'n',
            'include_variables_example': 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'background': ['sample_background_event'],
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config=config_provider, output_dir=tmpdir, overwrite=False)

        classname_prefix = data['project_slug'].replace('_', ' ').title().replace(' ', '')

        env_file_name = f".{data['project_slug']}_dev.env"

        env_file = open(os.path.join(tmpdir, data['project_slug'], env_file_name)).read()
        assert f'export API_KEY="{data["api_key"]}"' in env_file
        assert f'export ENVIRONMENT_ID="{data["environment_id"]}"' in env_file
        assert f'export SERVER_ADDRESS="{data["server_address"]}"' in env_file

        docker_compose_yml = yaml.safe_load(
            open(os.path.join(tmpdir, data['project_slug'], 'docker-compose.yml')),
        )

        for service_suffix in ('dev', 'bash', 'test'):
            service = docker_compose_yml['services'][f"{data['project_slug']}_{service_suffix}"]
            assert service['container_name'] == f"{data['project_slug']}_{service_suffix}"
            assert service['image'] == f'cloudblueconnect/connect-extension-runner:{runner_version}'
            assert service['env_file'] == [env_file_name]

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'webapp': f"{data['package_name']}.webapp:{classname_prefix}WebAppExtension",
        }

        parser = configparser.ConfigParser()
        parser.read(os.path.join(tmpdir, data['project_slug'], '.flake8'))

        assert parser['flake8']['application-import-names'] == data['package_name']

        flake8_style_guide = flake8.get_style_guide(
            show_source=parser['flake8']['show-source'],
            max_line_length=int(parser['flake8']['max-line-length']),
            application_import_names=parser['flake8']['application-import-names'],
            import_order_style=parser['flake8']['import-order-style'],
            max_cognitive_complexity=parser['flake8']['max-cognitive-complexity'],
            ignore=parser['flake8']['ignore'],
            exclude=parser['flake8']['exclude'],
        )
        report = flake8_style_guide.check_files([
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'webapp.py'),
        ])
        assert report.total_errors == 0

        webapp_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'webapp.py'),
        ).read()
        extension_json = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'extension.json'),
        ).read()

        assert 'from connect.eaas.core.extension import WebAppExtension' in webapp_py
        assert f'class {classname_prefix}WebAppExtension(WebAppExtension):' in webapp_py
        assert '@router.get' in webapp_py
        assert '"ui": {' in extension_json
        assert 'icon' in extension_json

        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'static_root'),
        ) is True
        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ) is False
        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'anvil.py'),
        ) is False


def test_bootstrap_extension_project_wizard_cancel(mocker):
    mocker.patch('connect.cli.plugins.project.extension.helpers.get_event_definitions')
    mocker.patch('connect.cli.plugins.project.extension.helpers.get_questions')
    mocker.patch('connect.cli.plugins.project.extension.helpers.get_summary')
    mocker.patch('connect.cli.plugins.project.extension.helpers.dialogus', return_value=None)

    with pytest.raises(ClickException) as cv:
        bootstrap_extension_project(None, 'dir', False)

    assert str(cv.value) == 'Aborted by user input'


def test_bootstrap_extension_project_if_destination_exists(mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocker.patch('connect.cli.plugins.project.extension.helpers.get_event_definitions', return_value=[])
        mocker.patch('connect.cli.plugins.project.extension.helpers.get_questions')
        mocker.patch('connect.cli.plugins.project.extension.helpers.get_summary')
        mocker.patch('connect.cli.plugins.project.extension.helpers.get_pypi_runner_version')
        project_folder = 'existing_folder'
        ctx = {
            'project_slug': project_folder,
            'extension_type': 'products',
            'base_dir': tmpdir,
            'background': {},
            'interactive': {},
        }
        mocker.patch('connect.cli.plugins.project.extension.helpers.dialogus', return_value=ctx)
        dst_dir = os.path.join(tmpdir, project_folder)
        os.makedirs(dst_dir)

        with pytest.raises(ClickException) as cv:
            bootstrap_extension_project(config=None, output_dir=tmpdir, overwrite=False)

        d = os.path.join(
            tmpdir,
            project_folder,
        )
        assert str(cv.value) == f'The destination directory {d} already exists.'


def test_bump_runner_version(mocker, capsys):
    _mock_pypi_version(mocker)
    docker_compose = {
        'services': {
            'dev': {'container_name': 'ext_dev', 'image': 'runner:0.5'},
            'test': {'container_name': 'ext_test', 'image': 'runner:0.5'},
        },
    }
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        with open(f'{project_dir}/docker-compose.yml', 'w') as fp:
            yaml.dump(docker_compose, fp)
        bump_runner_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'Runner version has been successfully updated' in captured.out


def test_bump_runner_docker_compose_not_found(mocker):
    _mock_pypi_version(mocker)
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        with pytest.raises(ClickException) as error:
            bump_runner_extension_project(project_dir)
        assert 'missing' in str(error.value)


def test_bump_runner_docker_yaml_error(mocker):
    _mock_pypi_version(mocker)
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        open(f'{project_dir}/docker-compose.yml', 'w').write(
            'services:\n\t{{cookiecutter.project_slug}}_dev:',
        )
        with pytest.raises(ClickException) as error:
            bump_runner_extension_project(project_dir)
        assert 'not properly formatted' in str(error.value)


def _mock_pypi_version(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
        return_value='1.0',
    )


def test_validate_extension_project(mocker, faker, mocked_responses, config_vendor, capsys):
    with tempfile.TemporaryDirectory() as tmpdir:
        runner_version = f'{faker.random_number()}.{faker.random_number()}'
        mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
            side_effect=runner_version,
        )
        mocker.patch(
            'connect.cli.plugins.project.extension.validations.get_pypi_runner_version',
            side_effect=runner_version,
        )
        config_vendor.load(config_dir='/tmp')

        mocked_responses.add(
            method='GET',
            url=f'{config_vendor.active.endpoint}/devops/event-definitions',
            headers={
                'Content-Range': 'items 0-0/1',
            },
            json=[
                {
                    'type': 'sample_background_event',
                    'group': 'Group',
                    'extension_type': 'products',
                    'name': 'Sample Event',
                    'category': 'background',
                    'object_statuses': ['status1', 'status2'],
                },
            ],
        )

        data = {
            'project_name': faker.name(),
            'project_slug': slugify(faker.name()),
            'extension_type': 'products',
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
            'include_schedules_example': 'y',
            'include_variables_example': 'y',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'background': ['sample_background_event'],
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config_vendor, tmpdir, False)

        project_dir = os.path.join(tmpdir, data['project_slug'])

        validate_extension_project(config_vendor, project_dir)

        captured = capsys.readouterr()
        assert 'has been successfully validated.' in captured.out.replace('\n', ' ')


def test_validate_extension_project_error_exit(mocker, faker, mocked_responses, config_vendor, capsys):
    runner_version = f'{faker.random_number()}.{faker.random_number()}'
    mocker.patch('connect.cli.plugins.project.extension.helpers.console.echo')
    mocker.patch(
        'connect.cli.plugins.project.extension.helpers.get_pypi_runner_version',
        side_effect=runner_version,
    )
    config_vendor.load(config_dir='/tmp')

    mocked_responses.add(
        method='GET',
        url=f'{config_vendor.active.endpoint}/devops/event-definitions',
        headers={
            'Content-Range': 'items 0-0/1',
        },
        json=[
            {
                'type': 'sample_background_event',
                'group': 'Group',
                'extension_type': 'products',
                'name': 'Sample Event',
                'category': 'background',
                'object_statuses': ['status1', 'status2'],
            },
        ],
    )

    data = {
        'project_name': faker.name(),
        'project_slug': slugify(faker.name()),
        'extension_type': 'products',
        'description': 'desc',
        'package_name': slugify(faker.name()),
        'author': 'connect',
        'version': '1.0',
        'license': 'Apache',
        'use_github_actions': 'n',
        'use_asyncio': 'n',
        'include_schedules_example': 'y',
        'include_variables_example': 'y',
        'api_key': faker.pystr(),
        'environment_id': f'ENV-{faker.random_number()}',
        'server_address': faker.domain_name(2),
        'background': ['sample_background_event'],
    }

    mocker.patch(
        'connect.cli.plugins.project.extension.helpers.dialogus',
        return_value=data,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = os.path.join(tmpdir, data['project_slug'])

        bootstrap_extension_project(config_vendor, tmpdir, False)

        os.unlink(os.path.join(project_dir, 'pyproject.toml'))

        validate_extension_project(config_vendor, project_dir)

        captured = capsys.readouterr()

        assert 'Warning/errors have been found' in captured.out
