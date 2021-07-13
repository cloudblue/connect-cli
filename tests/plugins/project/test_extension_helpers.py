#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import tempfile
from json.decoder import JSONDecodeError

import pytest
import toml
from click import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException
from pkg_resources import EntryPoint

from connect.cli.core.config import Config
from connect.cli.plugins.project.extension_helpers import (
    bootstrap_extension_project,
    validate_extension_project,
)
from connect.cli.plugins.project import utils


def _cookiecutter_result(local_path):
    os.makedirs(f'{local_path}/project_dir/connect_ext')
    open(f'{local_path}/project_dir/connect_ext/README.md', 'w').write('# Extension')


@pytest.mark.parametrize(
    'exists_cookiecutter_dir',
    (True, False),
)
def test_bootstrap_extension_project(
    fs,
    mocker,
    capsys,
    exists_cookiecutter_dir,
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
            'project_name': 'foo',
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
    assert mocked_dialogus.call_count == 6


def test_bootstrap_direxists_error(fs, mocker, config_mocker):
    config = Config()
    config.load(config_dir='/tmp')
    mocked_cookiecutter = mocker.patch(
        'connect.cli.plugins.project.extension_helpers.cookiecutter',
        side_effect=OutputDirExistsException('dir "project_dir" exists'),
    )
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.utils.dialogus',
        return_value={
            'project_name': 'foo',
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
    assert mocked_dialogus.call_count == 6


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


def test_validate_sync_project(mocker, capsys):
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
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )
    validate_extension_project(project_dir)

    captured = capsys.readouterr()
    assert 'successfully' in captured.out


def test_validate_async_project(mocker, capsys):
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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )
    validate_extension_project(project_dir)

    captured = capsys.readouterr()
    assert 'successfully' in captured.out


def test_validate_wrong_project_dir():
    project_dir = './tests'
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'does not look like an extension project directory' in str(error.value)


def test_validate_wrong_pyproject_file():
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        open(f'{tmp_project_dir}/pyproject.toml', 'w').write('foo')
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'The extension project descriptor file `pyproject.toml` is not valid.' in str(error.value)


def test_validate_wrong_plugin_declaration(mocked_extension_project_descriptor):
    pyproject_content = mocked_extension_project_descriptor
    pyproject_content['tool']['poetry']['plugins']['connect.eaas.ext'] = 'foo'
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        toml.dump(pyproject_content, open(f'{tmp_project_dir}/pyproject.toml', 'w'))
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'plugins."connect.eaas.ext"] `pyproject.toml` section is not well configured' in str(error.value)


def test_validate_plugin_with_no_extension_key(mocked_extension_project_descriptor):
    pyproject_content = mocked_extension_project_descriptor
    pyproject_content['tool']['poetry']['plugins']['connect.eaas.ext'] = {'newkey': 'pkg.extension:BasicExtension'}
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        toml.dump(pyproject_content, open(f'{tmp_project_dir}/pyproject.toml', 'w'))
        with pytest.raises(ClickException) as error:
            validate_extension_project(tmp_project_dir)

    assert 'plugins."connect.eaas.ext"] `pyproject.toml` section does not have "extension"' in str(error.value)


def test_validate_not_loaded():
    project_dir = './tests/fixtures/extensions/basic_ext'
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'The extension could not be loaded, Did you execute `poetry install`?' in str(error.value)


def test_validate_object_loaded_from_plugin_not_a_class(
    mocker,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    def _foo():
        pass

    mocked_load = mocker.patch.object(
        EntryPoint,
        'load',
        return_value=_foo,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        side_effect=JSONDecodeError('error', '', 0),
    )
    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'The extension descriptor file `extension.json` could not be loaded.' in str(error.value)


def test_validate_methods_not_match_capabilities(
    mocker,
):
    project_dir = './tests/fixtures/extensions/basic_ext'

    # On the extension project fixture there are 4 capabilities defined
    class BasicExtension:
        def process_asset_purchase_request(self):
            pass

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=BasicExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )

    with pytest.raises(ClickException) as error:
        validate_extension_project(project_dir)

    assert 'There is some mismatch between capabilities' in str(error.value)


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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
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

    mocker.patch.object(
        EntryPoint,
        'load',
        return_value=TestExtension,
    )
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.pkg_resources.iter_entry_points',
        return_value=iter([
            EntryPoint('extension', 'connect.eaas.ext'),
        ]),
    )
    mocked_extension_descriptor['capabilities'][capability] = ['approved']
    mocker.patch(
        'connect.cli.plugins.project.extension_helpers.json.load',
        return_value=mocked_extension_descriptor,
    )
    if capability == 'product_action_execution' or capability == 'product_custom_event_processing':
        with pytest.raises(ClickException) as error:
            validate_extension_project(project_dir)
        assert f'Capability `{capability}` must not have status.' in str(error.value)
    else:
        validate_extension_project(project_dir)
        captured = capsys.readouterr()
        assert 'successfully' in captured.out
