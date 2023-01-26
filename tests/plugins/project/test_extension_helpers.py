#  Copyright © 2022 CloudBlue. All rights reserved.

import configparser
import json
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
            'application_types': ['events'],
            'event_types': ['background'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'y' if with_github_actions else 'n',
            'use_asyncio': 'y' if async_impl else 'n',
            'include_variables_example': 'y' if with_variables else 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'background': ['sample_background_event'],
        }
        if with_schedulable:
            data['event_types'].append('scheduled')

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(
            config=config_vendor,
            output_dir=tmpdir,
            overwrite=False,
            load_answers=None,
            save_answers=None,
        )

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
            assert service['env_file'] == [env_file_name]

        docker_file = open(os.path.join(tmpdir, data['project_slug'], 'Dockerfile')).read()
        assert f'FROM cloudblueconnect/connect-extension-runner:{runner_version}' in docker_file

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'eventsapp': f"{data['package_name']}.events:{classname_prefix}EventsApplication",
        }

        if with_github_actions:
            assert os.path.exists(
                os.path.join(tmpdir, data['project_slug'], '.github', 'workflows', 'test.yml'),
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
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
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
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
        ).read()

        expected_test = test_bg_event(classname_prefix, async_impl=async_impl)
        print(expected_test)
        print(test_py)
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
            'application_types': ['events'],
            'event_types': ['interactive'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'y' if with_github_actions else 'n',
            'use_asyncio': 'y' if async_impl else 'n',
            'include_variables_example': 'y' if with_variables else 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
            'interactive': ['sample_interactive_event'],
        }
        if with_schedulable:
            data['event_types'].append('scheduled')

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        bootstrap_extension_project(config_vendor, tmpdir, False, None, None)

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
            assert service['env_file'] == [env_file_name]

        docker_file = open(os.path.join(tmpdir, data['project_slug'], 'Dockerfile')).read()
        assert f'FROM cloudblueconnect/connect-extension-runner:{runner_version}' in docker_file

        classname_prefix = data['project_slug'].replace('_', ' ').title().replace(' ', '')

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'eventsapp': f"{data['package_name']}.events:{classname_prefix}EventsApplication",
        }

        if with_github_actions:
            assert os.path.exists(
                os.path.join(tmpdir, data['project_slug'], '.github', 'workflows', 'test.yml'),
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
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
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
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
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
            'extension_audience': ['vendor', 'distributor'],
            'application_types': ['anvil', 'events'],
            'event_types': ['background', 'scheduled'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
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

        bootstrap_extension_project(
            config=config_vendor,
            output_dir=tmpdir,
            overwrite=False,
            load_answers=None,
            save_answers=f'{tmpdir}/sample.json',
        )

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
            assert service['env_file'] == [env_file_name]

        docker_file = open(os.path.join(tmpdir, data['project_slug'], 'Dockerfile')).read()
        assert f'FROM cloudblueconnect/connect-extension-runner:{runner_version}' in docker_file

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'anvilapp': f"{data['package_name']}.anvil:{classname_prefix}AnvilApplication",
            'eventsapp': f"{data['package_name']}.events:{classname_prefix}EventsApplication",
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
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_anvil.py'),
        ])
        assert report.total_errors == 0

        events_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'events.py'),
        ).read()
        anvil_py = open(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'anvil.py'),
        ).read()

        assert 'from connect.eaas.core.extension import EventsApplicationBase' in events_py
        assert f'class {classname_prefix}EventsApplication(EventsApplicationBase):' in events_py
        assert f'class {classname_prefix}AnvilApplication(AnvilApplicationBase):' in anvil_py

        assert extension_bg_event(async_impl=False) in events_py

        test_py = open(
            os.path.join(tmpdir, data['project_slug'], 'tests', 'test_events.py'),
        ).read()

        assert test_bg_event(classname_prefix, async_impl=False) in test_py

        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'webapp.py'),
        ) is False

        saved_answers = json.load(open(os.path.join(tmpdir, 'sample.json')))
        assert saved_answers == data


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
            'extension_audience': ['vendor', 'distributor'],
            'application_types': ['webapp'],
            'webapp_supports_ui': 'y',
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
            'include_variables_example': 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        with open(f'{tmpdir}/sample.json', 'w') as fp:
            json.dump({'project_name': 'Saved name', 'fake': 'fake'}, fp)

        bootstrap_extension_project(
            config=config_provider,
            output_dir=tmpdir,
            overwrite=False,
            load_answers=f'{tmpdir}/sample.json',
            save_answers=None,
        )

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
            assert service['env_file'] == [env_file_name]

        docker_file = open(os.path.join(tmpdir, data['project_slug'], 'Dockerfile')).read()
        assert f'FROM cloudblueconnect/connect-extension-runner:{runner_version}' in docker_file

        pyproject_toml = toml.load(os.path.join(tmpdir, data['project_slug'], 'pyproject.toml'))

        ext_entrypoint = pyproject_toml['tool']['poetry']['plugins']['connect.eaas.ext']
        assert ext_entrypoint == {
            'webapp': f"{data['package_name']}.webapp:{classname_prefix}WebApplication",
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

        assert 'from connect.eaas.core.extension import WebApplicationBase' in webapp_py
        assert f'class {classname_prefix}WebApplication(WebApplicationBase):' in webapp_py
        assert 'icon' in extension_json

        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'static', '.gitkeep'),
        ) is True
        assert os.path.exists(
            os.path.join(tmpdir, data['project_slug'], data['package_name'], 'schemas.py'),
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
        bootstrap_extension_project(None, 'dir', False, None, None)

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

        with open(f'{tmpdir}/sample.json', 'w') as fp:
            json.dump({'project_name': 'Saved'}, fp)

        with pytest.raises(ClickException) as cv:
            bootstrap_extension_project(
                config=None,
                output_dir=tmpdir,
                overwrite=False,
                load_answers=f'{tmpdir}/sample.json',
                save_answers=f'{tmpdir}/sample.json',
            )

        os.path.join(
            tmpdir,
            project_folder,
        )
        assert 'Answers cannot be saved' in str(cv.value)


def test_bump_runner_version(mocker, capsys):
    _mock_pypi_version(mocker)
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        docker_compose = {
            'services': {
                'dev': {'container_name': 'ext_dev', 'image': 'cloudblueconnect/connect-extension-runner:0.5'},
                'test': {'container_name': 'ext_test', 'image': 'cloudblueconnect/connect-extension-runner:0.5'},
                'si': {'container_name': 'ext_si', 'build': {'dockerfile': f'{project_dir}/OtherDockerfile'}},
                'prod': {'container_name': 'ext_prod', 'build': {'context': '.'}},
            },
        }
        with open(f'{project_dir}/docker-compose.yml', 'w') as fp:
            yaml.dump(docker_compose, fp)
        with open(f'{project_dir}/Dockerfile', 'w') as fp:
            fp.write('FROM cloudblueconnect/connect-extension-runner:0.5')
        with open(f'{project_dir}/OtherDockerfile', 'w') as fp:
            fp.write('FROM cloudblueconnect/connect-extension-runner:0.5')
        bump_runner_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'Runner version has been successfully updated to 1.0' in captured.out
        assert f'{os.path.join(project_dir, "docker-compose.yml")}' in captured.out
        assert f'{os.path.join(project_dir, "OtherDockerfile")}' in captured.out
        assert f'{os.path.join(project_dir, "Dockerfile")}' in captured.out


def test_bump_runner_version_no_update_required(mocker, capsys):
    _mock_pypi_version(mocker)
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        docker_compose = {
            'services': {
                'dev': {'container_name': 'ext_dev', 'image': 'cloudblueconnect/connect-extension-runner:1.0'},
                'test': {'container_name': 'ext_test', 'image': 'cloudblueconnect/connect-extension-runner:1.0'},
                'si': {'container_name': 'ext_si', 'build': {'dockerfile': f'{project_dir}/OtherDockerfile'}},
                'prod': {'container_name': 'ext_prod', 'build': {}},
            },
        }
        with open(f'{project_dir}/docker-compose.yml', 'w') as dc:
            yaml.dump(docker_compose, dc)
        with open(f'{project_dir}/Dockerfile', 'w') as df:
            df.write('FROM cloudblueconnect/connect-extension-runner:1.0')
            df.write('\n')
        with open(f'{project_dir}/OtherDockerfile', 'w') as df2:
            df2.write('FROM cloudblueconnect/connect-extension-runner:1.0')
            df2.write('\n')
        bump_runner_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'Nothing to update to 1.0' in captured.out


def test_bump_runner_version_invalid_dockerfile(mocker):
    _mock_pypi_version(mocker)
    docker_compose = {
        'services': {
            'dev': {
                'container_name': 'ext_dev',
                'build': {'dockerfile': 'invalidfile'},
            },
        },
    }
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        dc = f'{project_dir}/docker-compose.yml'
        with open(dc, 'w') as fp:
            yaml.dump(docker_compose, fp)
        with pytest.raises(ClickException) as exc:
            bump_runner_extension_project(project_dir)
        assert (
            f'The expected dockerfile `{project_dir}/invalidfile` specified in '
            f'{dc} is missing.'
        ) in str(exc)


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
            'application_types': ['events'],
            'event_type': ['background', 'scheduled'],
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
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

        bootstrap_extension_project(config_vendor, tmpdir, False, None, None)

        project_dir = os.path.join(tmpdir, data['project_slug'])

        validate_extension_project(config_vendor, project_dir)

        captured = capsys.readouterr()
        print(captured)
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
        'event_types': ['background', 'scheduled'],
        'description': 'desc',
        'package_name': slugify(faker.name()),
        'author': 'connect',
        'version': '1.0',
        'license': 'Apache',
        'use_github_actions': 'n',
        'use_asyncio': 'n',
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

        bootstrap_extension_project(config_vendor, tmpdir, False, None, None)

        os.unlink(os.path.join(project_dir, 'pyproject.toml'))

        validate_extension_project(config_vendor, project_dir)

        captured = capsys.readouterr()

        assert 'Warning/errors have been found' in captured.out


def test_bootstrap_extension_project_corrupted_load_answers(
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
            'extension_audience': ['vendor', 'distributor'],
            'application_types': ['webapp'],
            'webapp_supports_ui': 'y',
            'description': 'desc',
            'package_name': slugify(faker.name()),
            'author': 'connect',
            'version': '1.0',
            'license': 'Apache',
            'use_github_actions': 'n',
            'use_asyncio': 'n',
            'include_variables_example': 'n',
            'api_key': faker.pystr(),
            'environment_id': f'ENV-{faker.random_number()}',
            'server_address': faker.domain_name(2),
        }

        mocker.patch(
            'connect.cli.plugins.project.extension.helpers.dialogus',
            return_value=data,
        )

        with open(f'{tmpdir}/sample.json', 'w') as fp:
            fp.write('{"project_name": "Saved name", "fake": "fake"}, "error"')

        with pytest.raises(ClickException) as e:
            bootstrap_extension_project(
                config=config_provider,
                output_dir=tmpdir,
                overwrite=False,
                load_answers=f'{tmpdir}/sample.json',
                save_answers=None,
            )

        assert 'Can not load or parse answers' in str(e.value)
