#  Copyright © 2021 CloudBlue. All rights reserved.

import os

import pytest
from click import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException

from connect.cli.plugins.project.extension_helpers import bootstrap_extension_project
from connect.cli.plugins.project import utils


def _cookiecutter_result(local_path):
    os.makedirs(f'{local_path}/project_dir/connect_ext')
    open(f'{local_path}/project_dir/connect_ext/README.md', 'w').write('# Extension')


@pytest.mark.parametrize(
    'exists_cookiecutter_dir',
    (True, False),
)
def test_bootstrap_extension_project(fs, mocker, capsys, exists_cookiecutter_dir):
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
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    if exists_cookiecutter_dir:
        os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    output_dir = f'{fs.root_path}/projects'
    os.mkdir(output_dir)
    bootstrap_extension_project(output_dir)

    captured = capsys.readouterr()
    assert 'project_dir' in captured.out
    assert mocked_cookiecutter.call_count == 1
    assert mocked_dialogus.call_count == 5


def test_bootstrap_direxists_error(fs, mocker):
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
        bootstrap_extension_project(output_dir)
    assert mocked_cookiecutter.call_count == 1
    assert mocked_dialogus.call_count == 5


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
