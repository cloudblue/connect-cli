import pytest
from interrogatio.core.exceptions import ValidationError

from connect.cli.plugins.project.extension.validators import AppTypesValidator, UISupportValidator


@pytest.mark.parametrize(
    'app_types',
    (
        ['anvil'],
        ['events', 'webapp'],
        ['tfnapp'],
    ),
)
def test_app_types_validator_error(app_types):
    context = {
        'extension_type': 'transformations',
    }
    validator = AppTypesValidator()
    with pytest.raises(ValidationError):
        validator.validate(app_types, context)


def test_app_types_validator():
    context = {
        'extension_type': 'transformations',
    }
    validator = AppTypesValidator()
    assert validator.validate(['webapp', 'tfnapp'], context) is None


def test_ui_support_validator_error():
    context = {
        'extension_type': 'transformations',
    }
    validator = UISupportValidator()
    with pytest.raises(ValidationError):
        validator.validate('n', context)


def test_ui_support_validator():
    context = {
        'extension_type': 'transformations',
    }
    validator = UISupportValidator()
    assert validator.validate('y', context) is None
