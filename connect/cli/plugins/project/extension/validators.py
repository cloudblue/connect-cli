from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import Validator


class AppTypesValidator(Validator):
    def validate(self, value, context=None):
        if context.get('extension_type') == 'transformations' and (
            'webapp' not in value or 'tfnapp' not in value
        ):
            raise ValidationError(
                'Web Application and Transformations Application '
                'are mandatory for Commerce type extensions.',
            )


class UISupportValidator(Validator):
    def validate(self, value, context=None):
        if context.get('extension_type') == 'transformations' and value != 'y':
            raise ValidationError(
                'Web Application UI support is mandatory for Commerce type extensions.',
            )
