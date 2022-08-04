import pytest
from interrogatio.core.exceptions import ValidationError

from connect.cli.plugins.project.validators import get_code_context, PythonIdentifierValidator


@pytest.mark.parametrize(
    'identifier',
    (
        None,
        'snake_case_identifier',
        'CamelCase',
        'lowerCamelCase',
        'with123',
    ),
)
def test_python_identifier_validator(identifier):
    validator = PythonIdentifierValidator()
    assert validator.validate(identifier) is None


@pytest.mark.parametrize(
    'identifier',
    (
        ' ',
        'with spaces',
        '$invalid_symbol',
        'invalid_symbol%',
        '123numbers',
        '6789',
    ),
)
def test_python_identifier_validator_invalid(identifier):
    validator = PythonIdentifierValidator()
    with pytest.raises(ValidationError):
        validator.validate(identifier)


def test_get_code_context_module(mocker, faker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='path/file.py',
    )

    code_lines = [f'{line}\n' for line in faker.paragraphs(nb=10)]

    code = ''.join(code_lines)

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcelines',
        return_value=(
            code_lines,
            1,
        ),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.ismodule',
        return_value=True,
    )

    result = get_code_context(mocker.MagicMock(), 'country store build before')

    assert result['file'] == 'path/file.py'
    assert result['start_line'] == 1
    assert result['lineno'] == 7
    assert result['code'] == ''.join(code.splitlines(keepends=True)[0:7 + 3])


def test_get_code_context_function(mocker, faker):
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcefile',
        return_value='path/file.py',
    )

    code_lines = [f'{line}\n' for line in faker.paragraphs(nb=10)]

    code = ''.join(code_lines)

    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.getsourcelines',
        return_value=(
            code_lines,
            1,
        ),
    )
    mocker.patch(
        'connect.cli.plugins.project.extension.validations.inspect.ismodule',
        return_value=False,
    )

    result = get_code_context(mocker.MagicMock(), 'country store build before')

    assert result['file'] == 'path/file.py'
    assert result['start_line'] == 1
    assert result['lineno'] == 7
    assert result['code'] == ''.join(code.splitlines(keepends=True))
