#  Copyright © 2022 CloudBlue. All rights reserved.

import configparser
import os
import json
import tempfile

import pytest
import toml
from click import ClickException
from flake8.api import legacy as flake8

from connect.cli.plugins.project.report.helpers import (
    _add_report_to_descriptor,
    _entrypoint_validations,
    add_report,
    bootstrap_report_project,
    validate_report_project,
)


@pytest.mark.parametrize('with_github_actions', (True, False))
def test_bootstrap_report_project(mocker, capsys, with_github_actions):
    with tempfile.TemporaryDirectory() as tmpdir:
        data = {
            'project_name': 'foo',
            'project_slug': 'foobar',
            'package_name': 'bar',
            'initial_report_name': 'first',
            'initial_report_slug': 'initial_report_slug',
            'initial_report_renderer': 'json',
            'use_github_actions': 'y' if with_github_actions else 'n',
            'description': 'blabla',
            'version': '1.0',
            'author': 'James Bond',
            'license': 'mit',
        }
        mocked_dialogus = mocker.patch(
            'connect.cli.plugins.project.report.helpers.dialogus',
            return_value=data,
        )
        mocked_open = mocker.patch(
            'connect.cli.plugins.project.report.helpers.open',
            mocker.mock_open(read_data=str({})),
        )

        bootstrap_report_project(output_dir=tmpdir, overwrite=True)

        project_dir = os.path.join(tmpdir, data["project_slug"])
        mocked_open.assert_called_with(os.path.join(project_dir, 'HOWTO.md'), 'r')
        captured = capsys.readouterr()

        assert f'Folder /{data["project_slug"]} created' in captured.out
        assert f'Folder /{data["project_slug"]}/{data["package_name"]} created' in captured.out
        assert (
            f'Folder /{data["project_slug"]}/{data["package_name"]}/{data["initial_report_slug"]}'
            ' created'
        ) in captured.out
        assert mocked_dialogus.call_count == 1

        pyproject_toml = toml.load(
            os.path.join(
                tmpdir,
                data['project_slug'],
                'pyproject.toml',
            ),
        )

        report_pyp = pyproject_toml['tool']['poetry']

        assert report_pyp['name'] == data['project_slug']
        assert report_pyp['description'] == data['description']
        assert report_pyp['version'] == data['version']
        assert report_pyp['authors'] == [data['author']]
        assert report_pyp['license'] == data['license']
        assert report_pyp['packages'] == [{'include': data['package_name']}]
        assert pyproject_toml['tool']['pytest']['ini_options']['addopts'] == (
            f"--cov={data['package_name']} --cov-report=term-missing:skip-covered --cov-report=html --cov-report=xml"
        )

        assert os.path.exists(
            os.path.join(
                project_dir,
                '.github',
                'workflows',
                'build.yml',
            ),
        ) is with_github_actions

        parser = configparser.ConfigParser()
        parser.read(
            os.path.join(
                tmpdir,
                data['project_slug'],
                '.flake8',
            ),
        )

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
            os.path.join(project_dir, data['package_name'], 'reports.json'),
            os.path.join(project_dir, 'tests', f'test_{data["project_slug"]}.py'),
        ])
        assert report.total_errors == 0

        report_folder = (
            f"{project_dir}/{data['package_name']}/{data['initial_report_slug']}"
        )

        for path in (
            f"{report_folder}/templates",
            f"{report_folder}/templates/pdf",
            f"{report_folder}/templates/pdf/template.css",
            f"{report_folder}/templates/pdf/template.html.j2",
            f"{report_folder}/templates/xml",
            f"{report_folder}/templates/xml/template.xml.j2",
            f"{report_folder}/templates/xlsx",
            f"{report_folder}/__init__.py",
            f"{report_folder}/entrypoint.py",
            f"{report_folder}/README.md",
        ):
            assert os.path.exists(
                path,
            ), f'{path} does not exists: {os.listdir(report_folder)} {os.listdir(f"{report_folder}/templates")}'


def test_bootstrap_report_project_wizard_cancel(mocker):
    mocker.patch('connect.cli.plugins.project.report.helpers.dialogus', return_value=None)

    with pytest.raises(ClickException) as cv:
        bootstrap_report_project('dir', True)

    assert str(cv.value) == 'Aborted by user input'


def test_bootstrap_dir_exists_error(mocker):
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.report.helpers.dialogus',
        return_value={'project_slug': 'project'},
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = f'{tmpdir}/project'
        os.mkdir(output_dir)
        with pytest.raises(ClickException) as exc:
            bootstrap_report_project(tmpdir, False)
        assert str(exc.value) == f'The destination directory {tmpdir}/project already exists.'
        assert mocked_dialogus.call_count == 1


def test_validate_report_project(capsys):
    project_dir = './tests/fixtures/reports/basic_report'

    validate_report_project(project_dir)

    captured = capsys.readouterr()
    assert 'successfully' in captured.out


def test_validate_report_no_descriptor_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ClickException) as error:
            validate_report_project(tmpdir)
        assert 'the mandatory `reports.json` file descriptor is not present' in str(error.value)


def test_validate_report_wrong_descriptor_file(mocked_reports):
    wrong_data = f'{mocked_reports} - extrachar'
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/reports.json', 'w') as fp:
            fp.write(wrong_data)
        with pytest.raises(ClickException) as error:
            validate_report_project(f'{tmpdir}')
        assert str(error.value) == 'The report project descriptor `reports.json` is not a valid json file.'


def test_validate_report_schema(mocked_reports):
    wrong_data = mocked_reports
    # no valid value for 'reports' field
    wrong_data['reports'] = 'string'
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/reports.json', 'w') as fp:
            json.dump(wrong_data, fp)
        with pytest.raises(ClickException) as error:
            validate_report_project(f'{tmpdir}')
        assert 'Invalid `reports.json`: \'string\' is not of type' in str(error.value)


def test_validate_report_missing_files(mocked_reports):
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/reports.json', 'w') as fp:
            json.dump(mocked_reports, fp)

        # validate function will fail due to missing project files
        # like `readme.md` for instance, let's try it...
        with pytest.raises(ClickException) as error:
            validate_report_project(f'{tmpdir}')

        assert 'repository property `readme_file` cannot be resolved to a file' in str(error.value)


def test_entrypoint_wrong_import():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/entrypoint.py', 'w') as fp:
            fp.write('import foo')
        with pytest.raises(ClickException):
            _entrypoint_validations(tmpdir, 'entrypoint', '1')


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


def test_add_report_wrong_descriptor_project_file(mocker, mocked_reports):
    desc_validations_mocked = mocker.patch(
        'connect.cli.plugins.project.report.helpers._file_descriptor_validations',
        return_value=mocked_reports,
    )
    schema_validation_mocked = mocker.patch(
        'connect.cli.plugins.project.report.helpers.validate_with_schema',
        return_value=['error'],
    )

    with tempfile.TemporaryDirectory() as tmp_project_dir:
        os.makedirs(f'{tmp_project_dir}/project_dir/reports')
        with pytest.raises(ClickException) as error:
            add_report(f'{tmp_project_dir}/project_dir', 'reports')

    assert 'error' in str(error.value)
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1


def test_add_report_existing_repo_dir(mocker):
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        desc_validations_mocked = mocker.patch(
            'connect.cli.plugins.project.report.helpers._file_descriptor_validations',
            return_value=f'{tmp_project_dir}/project_dir',
        )
        schema_validation_mocked = mocker.patch(
            'connect.cli.plugins.project.report.helpers.validate_with_schema',
            return_value=[],
        )
        mocked_dialogus = mocker.patch(
            'connect.cli.plugins.project.report.helpers.dialogus',
            return_value={'initial_report_slug': 'report_dir'},
        )
        os.makedirs(f'{tmp_project_dir}/project_dir/reports/report_dir')
        with pytest.raises(ClickException) as error:
            add_report(f'{tmp_project_dir}/project_dir', package_name='reports')

    assert f'`{tmp_project_dir}/project_dir/reports/report_dir` already exists,' in str(error.value)
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1
    assert mocked_dialogus.call_count == 1


def test_add_report_empty_answers(mocker):
    with tempfile.TemporaryDirectory() as tmp_project_dir:
        desc_validations_mocked = mocker.patch(
            'connect.cli.plugins.project.report.helpers._file_descriptor_validations',
            return_value=f'{tmp_project_dir}/project_dir',
        )
        schema_validation_mocked = mocker.patch(
            'connect.cli.plugins.project.report.helpers.validate_with_schema',
            return_value=[],
        )
        mocked_dialogus = mocker.patch(
            'connect.cli.plugins.project.report.helpers.dialogus',
            return_value={},
        )
        os.makedirs(f'{tmp_project_dir}/project_dir/reports')
        with pytest.raises(ClickException) as error:
            add_report(f'{tmp_project_dir}/project_dir', package_name='reports')

    assert 'Aborted by user input' in str(error.value)
    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1
    assert mocked_dialogus.call_count == 1


def test_add_report(mocker, mocked_reports):
    desc_validations_mocked = mocker.patch(
        'connect.cli.plugins.project.report.helpers._file_descriptor_validations',
        return_value=mocked_reports,
    )
    schema_validation_mocked = mocker.patch(
        'connect.cli.plugins.project.report.helpers.validate_with_schema',
        return_value=[],
    )
    mocked_dialogus = mocker.patch(
        'connect.cli.plugins.project.report.helpers.dialogus',
        return_value={
            'initial_report_slug': 'report_dir',
            'project_slug': 'project_dir',
        },
    )
    add_report_mocked = mocker.patch(
        'connect.cli.plugins.project.report.helpers._add_report_to_descriptor',
    )

    with tempfile.TemporaryDirectory() as project_folder:
        project_dir = os.path.join(project_folder, 'project_dir')
        os.makedirs(os.path.join(project_dir, 'reports'))
        add_report(project_dir=project_dir, package_name='reports')

        report_dir = os.path.join(project_dir, 'reports', 'report_dir')

        for path in (
            report_dir,
            f"{report_dir}/templates",
            f"{report_dir}/templates/pdf",
            f"{report_dir}/templates/pdf/template.css",
            f"{report_dir}/templates/pdf/template.html.j2",
            f"{report_dir}/templates/xml",
            f"{report_dir}/templates/xml/template.xml.j2",
            f"{report_dir}/templates/xlsx",
            f"{report_dir}/__init__.py",
            f"{report_dir}/entrypoint.py",
            f"{report_dir}/README.md",
        ):
            assert os.path.exists(
                path,
            ), f'{path} does not exists'

        for path in (
            report_dir,
            f"{report_dir}/templates",
            f"{report_dir}/templates/pdf",
            f"{report_dir}/templates/xml",
            f"{report_dir}/templates/xlsx",
        ):
            assert os.path.isdir(
                path,
            ), f'{path} it is not a directory'

    assert desc_validations_mocked.call_count == 1
    assert schema_validation_mocked.call_count == 1
    assert mocked_dialogus.call_count == 1
    assert add_report_mocked.call_count == 1


def test_add_report_to_descriptor(mocked_reports):
    with tempfile.TemporaryDirectory() as tmp_data:
        project_dir = f'{tmp_data}/project_dir'
        os.mkdir(project_dir)
        with open(f'{project_dir}/reports.json', 'w') as fp:
            json.dump(mocked_reports, fp)
        ctx = {
            'initial_report_name': 'report',
            'initial_report_slug': '',
            'initial_report_renderer': 'pdf',
        }
        _add_report_to_descriptor(
            project_dir=project_dir,
            package_dir='reports',
            context=ctx,
        )
        with open(f'{project_dir}/reports.json', 'r') as fp:
            data = json.load(fp)
            assert len(data['reports']) == 2
