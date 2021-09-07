#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import tempfile
import json
from json.decoder import JSONDecodeError

import pytest
import toml
import yaml
from click import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.utils import work_in
from pkg_resources import EntryPoint

from connect.cli.core.config import Config
from connect.cli.plugins.project.extension_helpers import (
    _runner_version_validation,
    bootstrap_extension_project,
    bump_runner_extension_project,
    validate_extension_project,
)
from connect.cli.plugins.project import utils


def _cookiecutter_result(local_path):
    os.makedirs(f'{local_path}/project_dir/connect_ext')
    open(f'{local_path}/project_dir/connect_ext/README.md', 'w').write('# Extension')


@pytest.mark.parametrize('exists_cookiecutter_dir', (True, False))
@pytest.mark.parametrize('is_bundle', (True, False))
def test_bootstrap_extension_project(
    fs,
    mocker,
    capsys,
    exists_cookiecutter_dir,
    is_bundle,
    config_mocker,
):
    config = Config()
    config.load(config_dir='/tmp')
    mocked_cookiecutter = mocker.patch(
        'connect.cli.plugins.project.extension_helpers.cookiecutter',
        return_value='project_dir',
    )
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.utils.dialogus',
        return_value={
            'project_name': 'foo', 'description': 'desc',
            'package_name': 'bar', 'author': 'connect',
            'version': '1.0', 'license': 'Apache',
            'use_github_actions': 'y', 'use_asyncio': 'n',
            'api_key': 'xxx', 'environment_id': 'ENV-xxx',
            'server_address': 'api.cnct.info',
            'asset_processing': [],
            'asset_validation': [],
            'tierconfig': [],
            'product': [],
        },
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.open',
        mocker.mock_open(read_data='#Project'),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=is_bundle,
    )
    extension_json = {
        'name': 'my super project',
        'capabilities': {
            'asset_purchase_request_processing': ['draft'],
        },
    }
    mocked_open = mocker.patch(
        'connect.cli.plugins.project.utils.open',
        mocker.mock_open(read_data=str(extension_json)),
    )
    mocked_open = mocker.patch(
        'connect.cli.plugins.project.utils.json.load',
        return_value=mocked_open.return_value,
    )
    mocked_open = mocker.patch(
        'connect.cli.plugins.project.utils.json.dump',
        return_value=mocked_open.return_value,
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    if exists_cookiecutter_dir:
        os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    output_dir = f'{fs.root_path}/projects'
    os.mkdir(output_dir)
    bootstrap_extension_project(config, output_dir)

    captured = capsys.readouterr()
    assert 'project_dir' in captured.out
    assert mocked_cookiecutter.call_count == 1
    assert mocked_dialogus.call_count == 8


def test_bootstrap_dir_exists_error(fs, mocker, config_mocker):
    config = Config()
    config.load(config_dir='/tmp')
    mocked_cookiecutter = mocker.patch(
        'connect.cli.plugins.project.extension_helpers.cookiecutter',
        side_effect=OutputDirExistsException('dir "project_dir" exists'),
    )
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.utils.dialogus',
        return_value={
            'project_name': 'foo', 'description': 'desc',
            'package_name': 'bar', 'author': 'connect',
            'version': '1.0', 'license': 'Apache',
            'use_github_actions': 'y', 'use_asyncio': 'n',
            'api_key': 'xxx', 'environment_id': 'ENV-xxx',
            'server_address': 'api.cnct.info',
            'asset_processing': [],
            'asset_validation': [],
            'tierconfig': [],
            'product': [],
        },
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    output_dir = f'{fs.root_path}/projects'
    os.mkdir(output_dir)

    with pytest.raises(ClickException):
        bootstrap_extension_project(config, output_dir)
    assert mocked_cookiecutter.call_count == 1
    assert mocked_dialogus.call_count == 8


def test_bootstrap_show_empty_dialog(mocker):
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.utils.dialogus',
        return_value={},
    )
    with pytest.raises(ClickException):
        utils._show_dialog({}, 1, 5)

    assert mocked_dialogus.call_count == 1


def test_bootstrap_generate_capabilities():
    answers = {'asset': ['one', 'two']}
    cookiecutter_answers = utils._gen_cookie_capabilities(answers['asset'])

    assert cookiecutter_answers['one'] == 'y'
    assert cookiecutter_answers['two'] == 'y'


@pytest.mark.parametrize('is_bundle', (True, False))
def test_validate_sync_project(mocker, capsys, is_bundle):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class BasicExtension:
        def process_asset_purchase_request(self):
            pass

        def process_tier_config_setup_request(self):
            pass

        def execute_product_action(self):
            pass

        def process_product_custom_event(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=is_bundle,
    )
    if is_bundle:
        with pytest.raises(ClickException) as error:
            validate_extension_project(project_dir)
        assert 'This project can not be validated' in str(error.value)
    else:
        mocker.patch.object(
            EntryPoint,
            'load',
            return_value=BasicExtension,
        )
        mocker.patch(
            'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
            side_effect=(
                iter([EntryPoint('extension', 'connect.eaas.ext')]),
                iter([EntryPoint('extension', 'connect.eaas.ext')]),
            ),
        )

        _mock_pypi_version(mocker)
        validate_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'successfully' in captured.out


@pytest.mark.parametrize('is_bundle', (True, False))
def test_validate_async_project(mocker, capsys, is_bundle):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class BasicExtension:
        async def process_asset_purchase_request(self):
            pass

        async def process_tier_config_setup_request(self):
            pass

        async def execute_product_action(self):
            pass

        async def process_product_custom_event(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=is_bundle,
    )
    if is_bundle:
        with pytest.raises(ClickException) as error:
            validate_extension_project(project_dir)
        assert 'This project can not be validated' in str(error.value)
    else:
        mocker.patch.object(
            EntryPoint,
            'load',
            return_value=BasicExtension,
        )
        mocker.patch(
            'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
            side_effect=(
                iter([EntryPoint('extension', 'connect.eaas.ext')]),
                iter([EntryPoint('extension', 'connect.eaas.ext')]),
            ),
        )
        _mock_pypi_version(mocker)
        validate_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'successfully' in captured.out


def test_validate_too_much_extensions_loaded(mocker):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class BasicExtension:
        def process_asset_purchase_request(self):
            pass

        def process_tier_config_setup_request(self):
            pass

        def execute_product_action(self):
            pass

        def process_product_custom_event(self):
            pass

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'), EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'Only one extension can be loaded at a time!!!' in str(error.value)


def test_validate_wrong_project_dir(mocker):
    project_dir = './tests'
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'does not look like an extension project directory' in str(error.value)


def test_validate_wrong_pyproject_file(mocker):
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        open(f'{tmp_project_dir}/pyproject.toml', 'w').write('foo')
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'The extension project descriptor file `pyproject.toml` is not valid.' in str(error.value)


def test_validate_wrong_plugin_declaration(mocked_extension_project_descriptor, mocker):
    pyproject_content = mocked_extension_project_descriptor
    pyproject_content['tool']['poetry']['plugins']['connect.eaas.ext'] = 'foo'
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        toml.dump(pyproject_content, open(f'{tmp_project_dir}/pyproject.toml', 'w'))
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'plugins."connect.eaas.ext"] `pyproject.toml` section is not well configured' in str(error.value)


def test_validate_plugin_with_no_extension_key(mocked_extension_project_descriptor, mocker):
    pyproject_content = mocked_extension_project_descriptor
    pyproject_content['tool']['poetry']['plugins']['connect.eaas.ext'] = {'newkey': 'pkg.extension:BasicExtension'}
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        toml.dump(pyproject_content, open(f'{tmp_project_dir}/pyproject.toml', 'w'))
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'plugins."connect.eaas.ext"] `pyproject.toml` section does not have "extension"' in str(error.value)


def test_validate_not_loaded(mocker):
    project_dir = './tests/fixtures/extensions/basic_ext'
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'The extension could not be loaded, Did you execute `poetry install`?' in str(error.value)


def test_validate_object_loaded_from_plugin_not_a_class(
    mocker,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    def _foo():
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocked_load = mocker.patch.object(
        EntryPoint,
        'load',
        return_value=_foo,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert f'The extension class {mocked_load.return_value} does not seem a class' in str(error.value)


def test_validate_extension_json_descriptor(
    mocker,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class BasicExtension:
        pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        side_effect=JSONDecodeError('error', '', 0),
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'The extension descriptor file `extension.json` could not be loaded.' in str(error.value)


def test_validate_methods_not_match_capabilities(mocker):
    project_dir = './tests/fixtures/extensions/basic_ext'

    # On the extension project fixture there are 4 capabilities defined
    class BasicExtension:
        def process_asset_purchase_request(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )

    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'Capability-Method errors' in str(error.value)
    # The class defined above only implements 1 of the 4 capabilities
    # described on `basic_ext` fixture, then the list should contain 3
    # elements.
    assert len(str(error.value).split('[')[1].split(']')[0].split(',')) == 3


def test_validate_methods_mixed_sync_async(
    mocker,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class TestExtension:
        def process_asset_purchase_request(self):
            pass

        def process_tier_config_setup_request(self):
            pass

        async def execute_product_action(self):
            pass

        async def process_product_custom_event(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )

    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'An Extension class can only have sync or async methods not a mix of both.' in str(error.value)


def test_validate_capabilities_with_wrong_status(
    mocker,
    mocked_extension_descriptor,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class TestExtension:
        def process_asset_purchase_request(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )
    mocked_extension_descriptor['capabilities']['asset_purchase_request_processing'] = ['foo']
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        return_value=mocked_extension_descriptor,
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'Status `foo` on capability `asset_purchase_request_processing` is not allowed.' in str(error.value)


def test_validate_wrong_capability_without_status(
    mocker,
    mocked_extension_descriptor,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class TestExtension:
        def process_asset_purchase_request(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )
    mocked_extension_descriptor['capabilities']['asset_purchase_request_processing'] = []
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        return_value=mocked_extension_descriptor,
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'Capability `asset_purchase_request_processing` must have at least one allowed status.' in str(error.value)


@pytest.mark.parametrize(
    'capability',
    (
        'product_action_execution',
        'product_custom_event_processing',
        'asset_purchase_request_processing',
    ),
)
def test_validate_product_capability_with_status(
    mocker,
    mocked_extension_descriptor,
    capability,
    capsys,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    class TestExtension:
        def process_asset_purchase_request(self):
            pass

        def process_tier_config_setup_request(self):
            pass

        def execute_product_action(self):
            pass

        def process_product_custom_event(self):
            pass

    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.is_bundle',
        return_value=False,
    )
    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        side_effect=(
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
            iter([EntryPoint('extension', 'connect.eaas.ext')]),
        ),
    )
    mocked_extension_descriptor['capabilities'][capability] = ['approved']
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        return_value=mocked_extension_descriptor,
    )
    _mock_pypi_version(mocker)
    if capability == 'product_action_execution' or capability == 'product_custom_event_processing':
        with pytest.raises(ClickException) as error:
            validate_extension_project(project_dir)
        assert f'Capability `{capability}` must not have status.' in str(error.value)
    else:
        validate_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'successfully' in captured.out


@pytest.mark.parametrize(
    'package_name',
    ('good-one', 'wron@##)one'),
)
@pytest.mark.parametrize(
    'project_name',
    ('good-one', 'wron@##)one'),
)
def test_bootstrap_pre_gen_cookiecutter(project_name, package_name):
    answers = {'project_name': project_name, 'package_name': package_name}
    if project_name == 'wron@##)one' or package_name == 'wron@##)one':
        with pytest.raises(ClickException) as error:
            utils.pre_gen_cookiecutter_extension_hook(answers)
        assert 'slug is not a valid Python identifier' in str(error.value)


@pytest.mark.parametrize(
    ('answer', 'capability'),
    (
        ('subscription_process_capabilities_1of6', 'asset_purchase_request_processing'),
        ('subscription_process_capabilities_2of6', 'asset_change_request_processing'),
        ('subscription_process_capabilities_3of6', 'asset_suspend_request_processing'),
        ('subscription_process_capabilities_4of6', 'asset_resume_request_processing'),
        ('subscription_process_capabilities_5of6', 'asset_cancel_request_processing'),
        ('subscription_process_capabilities_6of6', 'asset_adjustment_request_processing'),
        ('subscription_validation_capabilities_1of2', 'asset_purchase_request_validation'),
        ('subscription_validation_capabilities_2of2', 'asset_change_request_validation'),
        ('tier_config_process_capabilities_1of3', 'tier_config_setup_request_processing'),
        ('tier_config_process_capabilities_2of3', 'tier_config_change_request_processing'),
        ('tier_config_process_capabilities_3of3', 'tier_config_adjustment_request_processing'),
        ('tier_config_validation_capabilities_1of2', 'tier_config_setup_request_validation'),
        ('tier_config_validation_capabilities_2of2', 'tier_config_change_request_validation'),
        ('product_capabilities_1of2', 'product_action_execution'),
        ('product_capabilities_2of2', 'product_custom_event_processing'),
    ),
)
def test_post_gen_cookiecutter_hook(mocker, answer, capability):
    mocker.patch(
        'connect.cli.plugins.project.utils.os.remove',
    )
    mocker.patch(
        'connect.cli.plugins.project.utils.shutil.rmtree',
    )
    answers = {
        'project_name': 'project',
        'package_name': 'package',
        'license': 'Other, not Open-source',
        'use_github_actions': 'n',
        answer: 'y',
    }
    extension_json = {
        'name': 'my super project',
        'capabilities': {},
    }
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = os.mkdir(f'{tmp_data}/project')
        os.mkdir(f'{tmp_data}/project/package')
        with open(f'{tmp_data}/project/package/extension.json', 'w') as fp:
            json.dump(extension_json, fp)
        with work_in(f'{tmp_data}'):
            utils.post_gen_cookiecutter_extension_hook(answers, project_dir)

        with open(f'{tmp_data}/project/package/extension.json', 'r') as fp:
            data = json.load(fp)

        assert capability in data['capabilities'].keys()
        assert isinstance(data['capabilities'][capability], list)
        if answer == 'product_capabilities_1of2' or answer == 'product_capabilities_2of2':
            assert data['capabilities'][capability] == []
        else:
            assert data[
                'capabilities'
            ][capability] == ['draft', 'tiers_setup', 'pending', 'inquiring', 'approved', 'failed']


def test_validate_runner_ok(mocker, capsys):
    _mock_pypi_version(mocker)
    docker_compose = {
        'services': {
            'dev': {'container_name': 'ext_dev', 'image': 'runner:1.0'},
            'test': {'container_name': 'ext_test', 'image': 'runner:1.0'},
        },
    }
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        with open(f'{project_dir}/docker-compose.yml', 'w') as fp:
            yaml.dump(docker_compose, fp)

        _runner_version_validation(project_dir)

        captured = capsys.readouterr()
        assert captured.out == ''


def test_validate_runner_pypi_not_reached(mocker, capsys):
    res = mocker.MagicMock()
    res.status_code = 404
    res.json.return_value = {'info': {'version': '1.0'}}
    mocked_get = mocker.patch(
        'connect.cli.plugins.project.extension_helpers.requests.get',
        return_value=res,
    )
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)

        with pytest.raises(ClickException) as error:
            _runner_version_validation(project_dir)

    assert mocked_get.call_count == 1
    assert 'can not retrieve' in str(error.value)


def test_validate_runner_pypi_not_json(mocker, capsys):
    res = mocker.MagicMock()
    res.status_code = 200
    res.json.return_value = 'foo'
    mocked_get = mocker.patch(
        'connect.cli.plugins.project.extension_helpers.requests.get',
        return_value=res,
    )
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)

        with pytest.raises(ClickException) as error:
            _runner_version_validation(project_dir)

    assert mocked_get.call_count == 1
    assert 'content retrieved' in str(error.value)


def test_validate_runner_docker_compose_not_found(mocker):
    _mock_pypi_version(mocker)

    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)

        with pytest.raises(ClickException) as error:
            _runner_version_validation(project_dir)

    assert 'missing' in str(error.value)


def test_validate_runner_docker_yaml_error(mocker):
    _mock_pypi_version(mocker)
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        open(f'{project_dir}/docker-compose.yml', 'w').write(
            'services:\n\t{{cookiecutter.project_slug}}_dev:',
        )
        with pytest.raises(ClickException) as error:
            _runner_version_validation(project_dir)

    assert 'not properly formatted' in str(error.value)


def test_validate_runner_version_mismatch(mocker):
    _mock_pypi_version(mocker)
    docker_compose = {
        'services': {
            'dev': {'container_name': 'ext_dev', 'image': 'runner:0.1'},
            'test': {'container_name': 'ext_test', 'image': 'runner:0.1'},
        },
    }
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project'
        os.mkdir(project_dir)
        with open(f'{project_dir}/docker-compose.yml', 'w') as fp:
            yaml.dump(docker_compose, fp)
            with pytest.raises(ClickException) as error:
                _runner_version_validation(project_dir)

    assert 'file is not the latest one' in str(error.value)


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
    res = mocker.MagicMock()
    res.status_code = 200
    res.json.return_value = {'info': {'version': '1.0'}}
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.requests.get',
        return_value=res,
    )
