#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import json

import pytest

from click import ClickException

from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException

from connect.cli.plugins.project.helpers import (
    _entrypoint_validations,
    add_report,
    bootstrap_project,
    list_projects,
    validate_project,
)


def test_bootstrap_project(fs, mocker, capsys):
    mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        return_value='project_dir',
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    data_dir = f'{fs.root_path}/projects'
    os.mkdir(data_dir)
    bootstrap_project(data_dir)

    captured = capsys.readouterr()
    assert 'project_dir' in captured.out


def test_bootstrap_direxists_error(fs, mocker):
    mocked_cookiecutter = mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        side_effect=OutputDirExistsException('dir "project_dir" exists'),
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    data_dir = f'{fs.root_path}/projects'
    os.mkdir(data_dir)

    with pytest.raises(ClickException):
        bootstrap_project(data_dir)
    assert mocked_cookiecutter.call_count == 1


def test_list_projects_empty_dir(fs, mocker, capsys):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=[],
    )
    list_projects(fs.root_path)

    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    captured = capsys.readouterr()
    assert 'No projects found!' in captured.out


def test_list_projects_wrong_json(fs, mocker):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=['project1/reports.json'],
    )
    mocker.patch(
        'connect.cli.plugins.project.helpers.open',
        return_value='super-duper content',
    )
    mocked_load = mocker.patch(
        'connect.cli.plugins.project.helpers.json.load',
        side_effect=json.JSONDecodeError(msg='error', doc='error', pos=1),
    )
    with pytest.raises(ClickException):
        list_projects(fs.root_path)
    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    mocked_load.assert_called_once_with('super-duper content')


def test_list_projects(fs, mocker, mocked_reports, capsys):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=['project1/reports.json'],
    )
    project_one = mocked_reports
    mocker.patch(
        'connect.cli.plugins.project.helpers.open',
    )
    mocker.patch(
        'connect.cli.plugins.project.helpers.json.load',
        return_value=project_one,
    )
    list_projects(fs.root_path)

    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    captured = capsys.readouterr()
    assert 'Connect Reports' in captured.out


def test_validate_project(capsys):
    project_dir = './tests/fixtures/reports/basic_report'

    validate_project(project_dir)

    captured = capsys.readouterr()
    assert 'successfully' in captured.out


def test_validate_no_descriptor_file(fs):
    with pytest.raises(ClickException) as error:
        validate_project(fs.root_path)

    assert 'the mandatory `reports.json` file descriptor is not present' in str(error.value)


def test_validate_wrong_descriptor_file(fs, mocked_reports):
    wrong_data = f'{mocked_reports} - extrachar'

    with open(f'{fs.root_path}/reports.json', 'w') as fp:
        fp.write(wrong_data)

    with pytest.raises(ClickException) as error:
        validate_project(f'{fs.root_path}')

    assert str(error.value) == 'The report project descriptor `reports.json` is not a valid json file.'


def test_validate_schema(fs, mocked_reports):
    wrong_data = mocked_reports
    # no valid value for 'reports' field
    wrong_data['reports'] = 'string'

    with open(f'{fs.root_path}/reports.json', 'w') as fp:
        json.dump(wrong_data, fp)

    with pytest.raises(ClickException) as error:
        validate_project(f'{fs.root_path}')

    assert 'Invalid `reports.json`: \'string\' is not of type' in str(error.value)


def test_validate_missing_files(fs, mocked_reports):
    with open(f'{fs.root_path}/reports.json', 'w') as fp:
        json.dump(mocked_reports, fp)

    # validate function will fail due to missing project files
    # like `readme.md` for instance, let's try it...
    with pytest.raises(ClickException) as error:
        validate_project(f'{fs.root_path}')

    assert 'repository property `readme_file` cannot be resolved to a file' in str(error.value)


def test_entrypoint_wrong_import(fs):
    with open(f'{fs.root_path}/entrypoint.py', 'w') as fp:
        fp.write('import foo')

    with pytest.raises(ClickException):
        _entrypoint_validations(fs.root_path, 'entrypoint', '1')


@pytest.mark.parametrize(
    'spec_version',
    ('1', '2'),
)
def test_entrypoint_wrong_signature(fs, spec_version):
    with open(f'{fs.root_path}/wrong_signature.py', 'w') as bad_signature:
        bad_signature.write('def generate(client, parameters): pass')

    with pytest.raises(ClickException):
        _entrypoint_validations(fs.root_path, 'wrong_signature', spec_version)


def test_add_report(fs, mocker):

    def cookiecutter_result(local_path):
        os.mkdir(f'{local_path}/report_dir')
        open(f'{local_path}/report_dir/Readme.md', 'w').write('# Report')

    cookie_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        side_effect=cookiecutter_result(fs.root_path),
        return_value=f'{fs.root_path}/report_dir',
    )

    assert os.path.isdir(cookie_mocked.return_value)
    assert os.path.isfile(f'{cookie_mocked.return_value}/Readme.md')

    import tempfile
    with tempfile.TemporaryDirectory() as project_dir:
        os.mkdir(f'{project_dir}/reports')
        add_report(project_dir)
        assert os.path.isdir(f'{project_dir}/reports/report_dir')

    assert cookie_mocked.call_count == 1
