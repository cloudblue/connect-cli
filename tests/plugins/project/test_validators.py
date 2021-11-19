import pytest
from interrogatio.core.exceptions import ValidationError

from connect.cli.plugins.project.validators import PythonIdentifierValidator


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
