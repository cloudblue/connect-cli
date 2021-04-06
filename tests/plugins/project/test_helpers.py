#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import json
import tempfile

import pytest
from click import ClickException
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException

from connect.cli.plugins.project.helpers import (
    _add_report_to_descriptor,
    _custom_cookiecutter,
    _entrypoint_validations,
    add_report,
    bootstrap_project,
    validate_project,
)


def _cookiecutter_result(local_path):
    os.makedirs(f'{local_path}/project_dir/reports/report_dir')
    open(f'{local_path}/project_dir/reports/report_dir/README.md', 'w').write('# Report')


@pytest.mark.parametrize(
    'exists_cookiecutter_dir',
    (True, False),
)
def test_bootstrap_project(fs, mocker, capsys, exists_cookiecutter_dir):
    mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        return_value='project_dir',
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    if exists_cookiecutter_dir:
        os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    output_dir = f'{fs.root_path}/projects'
    os.mkdir(output_dir)
    bootstrap_project(output_dir)

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

    output_dir = f'{fs.root_path}/projects'
    os.mkdir(output_dir)

    with pytest.raises(ClickException):
        bootstrap_project(output_dir)
    assert mocked_cookiecutter.call_count == 1


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


def test_add_report_no_package_dir(fs):
    os.mkdir(f'{fs.root_path}/project_dir')
    package_name = 'reports'
    with pytest.raises(ClickException):
        add_report(f'{fs.root_path}/project_dir', package_name)


def test_add_report_wrong_descriptor_project_file(fs, mocker, mocked_reports):
    desc_validations_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._file_descriptor_validations',
        return_value=mocked_reports,
    )
    schema_validation_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.validate_with_schema',
        return_value=['error'],
    )

    with tempfile.TemporaryDirectory() as tmp_project_dir:
        os.makedirs(f'{tmp_project_dir}/project_dir/reports')
        with pytest.raises(ClickException) as error:
            add_report(f'{tmp_project_dir}/project_dir', 'reports')

    assert 'error' in str(error.value)
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1


def test_add_report_existing_repo_dir(fs, mocker, mocked_reports):
    desc_validations_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._file_descriptor_validations',
        return_value=mocked_reports,
    )
    schema_validation_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.validate_with_schema',
        return_value=[],
    )
    cookie_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._custom_cookiecutter',
        side_effect=_cookiecutter_result(fs.root_path),
        return_value=(f'{fs.root_path}/project_dir', 'report_dir'),
    )
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        os.makedirs(f'{tmp_project_dir}/project_dir/reports/report_dir')
        with pytest.raises(ClickException) as error:
            add_report(f'{tmp_project_dir}/project_dir', package_name='reports')

    assert f'`{tmp_project_dir}/project_dir/reports/report_dir` already exists,' in str(error.value)
    assert cookie_mocked.call_count == 1
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1


def test_add_report(fs, mocker, mocked_reports):
    desc_validations_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._file_descriptor_validations',
        return_value=mocked_reports,
    )
    schema_validation_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.validate_with_schema',
        return_value=[],
    )
    cookie_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._custom_cookiecutter',
        side_effect=_cookiecutter_result(fs.root_path),
        return_value=(f'{fs.root_path}/project_dir', 'report_dir'),
    )

    assert os.path.isdir(cookie_mocked.return_value[0])
    assert os.path.isfile(f'{cookie_mocked.return_value[0]}/reports/report_dir/README.md')

    cookie_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers._add_report_to_descriptor',
    )

    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir
    with tempfile.TemporaryDirectory() as project_dir:
        os.mkdir(f'{project_dir}/reports')
        add_report(project_dir, package_name='reports')
        assert os.path.isdir(f'{project_dir}/reports/report_dir')

    assert cookie_mocked.call_count == 1
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1


def test_add_report_to_descriptor(fs, mocked_reports, mocker):
    _cookiecutter_result(fs.root_path)
    with open(f'{fs.root_path}/project_dir/reports.json', 'w') as fp:
        json.dump(mocked_reports, fp)

    with tempfile.TemporaryDirectory() as tmp_data:
        os.mkdir(f'{tmp_data}/project_dir')
        with open(f'{tmp_data}/project_dir/reports.json', 'w') as fp:
            json.dump(mocked_reports, fp)

        _add_report_to_descriptor(
            f'{tmp_data}/project_dir',
            f'{fs.root_path}/project_dir',
            'reports',
        )
        with open(f'{tmp_data}/project_dir/reports.json', 'r') as fp:
            data = json.load(fp)

            assert len(data['reports']) == 2


def test_custom_cookiecutter(fs, mocker):
    cookiecutter_json_content = {
        'project_name': 'project name',
        'project_slug': 'project_name',
        'package_name': 'reports',
        'initial_report_name': 'report name',
        'initial_report_slug': 'initial_report_name',
        'initial_report_description': 'desc',
        'author': 'me',
    }
    report_context = {
        'report_name': 'report name',
        'report_slug': 'report_name',
        'report_description': 'desc',
        'author': 'me',
    }

    config_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.get_user_config',
    )
    mocker.patch(
        'connect.cli.plugins.project.helpers.rmtree',
    )
    repo_dir_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.determine_repo_dir',
    )
    generate_context_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.generate_context',
        return_value={
            'cookiecutter': cookiecutter_json_content,
        },
    )
    prompt_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.prompt_for_config',
        return_value=report_context,
    )
    generate_files_mocked = mocker.patch(
        'connect.cli.plugins.project.helpers.generate_files',
        return_value=f'{fs.root_path}/project_name',
    )

    with tempfile.TemporaryDirectory() as cookiedir_tmp:
        template = f'{cookiedir_tmp}/boilerplate'
        os.mkdir(template)
        json.dump(
            cookiecutter_json_content,
            open(f'{template}/cookiecutter.json', 'w'),
        )
        repo_dir_mocked.return_value = (template, False)
        config_mocked.return_value = {
            'cookiecutters_dir': f'{cookiedir_tmp}',
            'abbreviations': ['gh'],
            'default_context': None,
        }

        report_dir, report_slug = _custom_cookiecutter(template, fs.root_path)

    assert report_slug == 'report_name'
    assert report_dir == f'{fs.root_path}/project_name'
    assert repo_dir_mocked.call_count == 1
    assert generate_context_mocked.call_count == 1
    assert prompt_mocked.call_count == 1
    assert generate_files_mocked.call_count == 1
    assert config_mocked.call_count == 1
