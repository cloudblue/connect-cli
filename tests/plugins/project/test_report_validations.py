import os
import tempfile

import pytest

from connect.cli.plugins.project.validators import ValidationItem, ValidationResult
from connect.cli.plugins.project.report.validations import (
    _load_reports_json,
    _validate_entrypoint,
    validate_pyproject_toml,
    validate_report_json_with_schema,
    validate_reports_json,
    validate_repository_definition,
)


def test_entrypoint_wrong_import(mocker):
    mocker.patch(
        'connect.cli.plugins.project.report.validations.importlib.import_module',
        side_effect=ImportError('error'),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f'{tmpdir}/entrypoint.py', 'w') as fp:
            fp.write('import foo')
        result = _validate_entrypoint(tmpdir, 'some.entrypoint', '1')
        assert isinstance(result, ValidationItem)
        assert result.level == 'ERROR'
        assert result.message == '\nErrors detected on entrypoint module: error'


def test_entrypoint_wrong_signature_v1():
    with tempfile.TemporaryDirectory() as tmp:
        file = os.path.join(tmp, 'wrong_signature.py')
        with open(file, 'w') as bad_signature:
            bad_signature.write('def generate(client, parameters): pass')
        result = _validate_entrypoint(tmp, 'wrong_signature', '1')
        assert isinstance(result, ValidationItem)
        assert result.level == 'ERROR'
        assert result.message == (
            'Wrong arguments on `generate` function. The signature must be:'
            '\n`def generate(client, parameters, progress_callback)`'
        )
        assert result.file == file
        assert result.start_line == 1
        assert result.lineno == 1


def test_entrypoint_wrong_signature_v2():
    with tempfile.TemporaryDirectory() as tmp:
        file = os.path.join(tmp, 'wrong_signature_v2.py')
        with open(file, 'w') as bad_signature:
            bad_signature.write('def generate(client, parameters): pass')
        result = _validate_entrypoint(tmp, 'wrong_signature_v2', '2')
        assert isinstance(result, ValidationItem)
        assert result.level == 'ERROR'
        assert result.message == (
            'Wrong arguments on `generate` function. The signature must be:'
            '\n`def generate(client=None, input_data=None, progress_callback=None, '
            'renderer_type=None, extra_context_callback=None)`'
        )
        assert result.file == file
        assert result.start_line == 1
        assert result.lineno == 1


def test_validate_reports_json_no_file():
    assert validate_reports_json('anydirectory', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    'ERROR',
                    'The directory `anydirectory` does not look like a report project '
                    'directory, the mandatory `reports.json` file descriptor is not '
                    'present.',
                ),
            ],
            must_exit=True,
        )
    )


def test_validate_reports_json_invalid_file():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'reports.json'), 'a') as f:
            f.write("content")
            f.close()
            assert validate_reports_json(tmp, None) == (
                ValidationResult(
                    items=[
                        ValidationItem(
                            'ERROR',
                            'The report project descriptor `reports.json` is not a valid json '
                            'file.',
                        ),
                    ],
                    must_exit=True,
                )
            )


def test_validate_report_json_with_schema(mocker):
    mocker.patch(
        'connect.cli.plugins.project.report.validations._load_reports_json',
        return_value={'valid': 'json'},
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.validate_with_schema',
        return_value=['error'],
    )
    assert validate_report_json_with_schema('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    level='ERROR',
                    message=['error'],
                ),
            ],
            must_exit=True,
        )
    )


def test_validate_report_json_with_schema_no_error(mocker):
    mocker.patch(
        'connect.cli.plugins.project.report.validations._load_reports_json',
        return_value={'valid': 'json'},
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.validate_with_schema',
        return_value=[],
    )
    assert validate_report_json_with_schema('any', {}) == (
        ValidationResult(
            items=[],
            must_exit=False,
        )
    )


def test_validate_repository_definition_validate_error(mocker):
    mocker.patch('connect.cli.plugins.project.report.validations._load_reports_json')
    mocker.patch('connect.cli.plugins.project.report.validations.parse')
    mocker.patch('connect.cli.plugins.project.report.validations.validate', return_value=['error1'])
    assert validate_repository_definition('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    level='ERROR',
                    message=error,
                ) for error in ['error1']],
            must_exit=True,
        )
    )


def test_validate_repository_definition_error_on_report_entrypoint(mocker):
    mocker.patch('connect.cli.plugins.project.report.validations._load_reports_json')
    mocked_parse = mocker.MagicMock()
    mocked_report = mocker.MagicMock()
    mocked_report.entrypoint = 'some.entry.point'
    mocked_report.report_spec = '1'
    mocked_parse.reports = [mocked_report]
    mocker.patch('connect.cli.plugins.project.report.validations.parse', return_value=mocked_parse)
    mocker.patch('connect.cli.plugins.project.report.validations.validate', return_value=[])
    mocker.patch(
        'connect.cli.plugins.project.report.validations._validate_entrypoint',
        return_value=ValidationItem(
            'ERROR',
            '\nErrors detected on entrypoint module: error1',
        ),
    )
    assert validate_repository_definition('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    'ERROR',
                    '\nErrors detected on entrypoint module: error1',
                ),
            ],
            must_exit=True,
        )
    )


def test_validate_repository_definition_success_on_specs_v2(mocker):
    mocker.patch('connect.cli.plugins.project.report.validations._load_reports_json')
    mocked_parse = mocker.MagicMock()
    mocked_report = mocker.MagicMock()
    mocked_report.entrypoint = 'some.entry.point'
    mocked_report.report_spec = '2'
    mocked_parse.reports = [mocked_report]
    mocker.patch('connect.cli.plugins.project.report.validations.parse', return_value=mocked_parse)
    mocker.patch('connect.cli.plugins.project.report.validations.validate', return_value=[])
    mocker.patch('connect.cli.plugins.project.report.validations.len', return_value=5)
    mocker.patch('connect.cli.plugins.project.report.validations.importlib.import_module')
    mocker.patch('connect.cli.plugins.project.report.validations.inspect')

    assert validate_repository_definition('any', {}) == (
        ValidationResult(
            items=[],
            must_exit=False,
        )
    )


def test_validate_repository_definition_success(mocker):
    mocker.patch('connect.cli.plugins.project.report.validations._load_reports_json')
    mocked_parse = mocker.MagicMock()
    mocked_report = mocker.MagicMock()
    mocked_report.entrypoint = 'some.entry.point'
    mocked_report.report_spec = '1'
    mocked_parse.reports = [mocked_report]
    mocker.patch('connect.cli.plugins.project.report.validations.parse', return_value=mocked_parse)
    mocker.patch('connect.cli.plugins.project.report.validations.validate', return_value=[])
    mocker.patch(
        'connect.cli.plugins.project.report.validations._validate_entrypoint',
        return_value=[],
    )
    assert validate_repository_definition('any', {}) == (
        ValidationResult(
            items=[],
            must_exit=False,
        )
    )


def test_load_reports_json():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'reports.json'), 'a') as f:
            f.write('{"hello": "world"}')
            f.close()
        assert _load_reports_json(tmp) == {'hello': 'world'}


def test_validate_pyproject_toml_error_loading(mocker):
    result = ValidationResult([])
    mocker.patch(
        'connect.cli.plugins.project.report.validations.load_project_toml_file',
        return_value=result,
    )
    assert validate_pyproject_toml('any', {}) == result


def test_validate_pyproject_toml_warning_no_connect_cli(mocker):
    mocker.patch(
        'connect.cli.plugins.project.report.validations.os.path.join',
        return_value='/descriptor_file/pyproject.toml',
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.load_project_toml_file',
        return_value={
            'tool': {
                'poetry': {
                    'dev-dependencies': {},
                },
            },
        },
    )
    assert validate_pyproject_toml('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    'WARNING',
                    'No development dependency on *connect-cli* has been found.',
                    '/descriptor_file/pyproject.toml',
                ),
            ],
            must_exit=False,
        )
    )


def test_validate_pyproject_toml_warning_error_on_getting_last_version(mocker):
    mocker.patch(
        'connect.cli.plugins.project.report.validations.os.path.join',
        return_value='/descriptor_file/pyproject.toml',
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.load_project_toml_file',
        return_value={
            'tool': {
                'poetry': {
                    'dev-dependencies': {'connect-cli': '^24.1'},
                },
            },
        },
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.get_last_cli_version',
        return_value=None,
    )
    assert validate_pyproject_toml('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    'WARNING',
                    'The version ^24.1 specified in your pyproject.toml cannot be verified '
                    'to include the lastest connect-cli.',
                    '/descriptor_file/pyproject.toml',
                ),
            ],
            must_exit=False,
        )
    )


@pytest.mark.parametrize(
    ('specified', 'last_version'),
    (
        ('^24.1', '25.2'),
        ('<=24.5', '24.6'),
        ('24.3', '24.4'),
    ),
)
def test_validate_pyproject_toml_warning_connect_cli_update(mocker, specified, last_version):
    mocker.patch(
        'connect.cli.plugins.project.report.validations.os.path.join',
        return_value='/descriptor_file/pyproject.toml',
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.load_project_toml_file',
        return_value={
            'tool': {
                'poetry': {
                    'dev-dependencies': {'connect-cli': specified},
                },
            },
        },
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.get_last_cli_version',
        return_value=last_version,
    )
    assert validate_pyproject_toml('any', {}) == (
        ValidationResult(
            items=[
                ValidationItem(
                    'WARNING',
                    f'The version range {specified} specified in your '
                    'pyproject.toml does not include the lastest connect-cli version which is '
                    f'{last_version}.',
                    '/descriptor_file/pyproject.toml',
                ),
            ],
            must_exit=False,
        )
    )


@pytest.mark.parametrize(
    ('specified', 'last_version'),
    (
        ('^24.1', '24.2'),
        ('>24.1', '25.2'),
        ('>24,<25', '24.3'),
    ),
)
def test_validate_pyproject_toml_success(mocker, specified, last_version):
    mocker.patch(
        'connect.cli.plugins.project.report.validations.os.path.join',
        return_value='/descriptor_file/pyproject.toml',
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.load_project_toml_file',
        return_value={
            'tool': {
                'poetry': {
                    'dev-dependencies': {'connect-cli': specified},
                },
            },
        },
    )
    mocker.patch(
        'connect.cli.plugins.project.report.validations.get_last_cli_version',
        return_value=last_version,
    )
    assert validate_pyproject_toml('any', {}) == (
        ValidationResult(
            items=[],
        )
    )
