from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import Validator


class PythonIdentifierValidator(Validator):

    def validate(self, value, context=None):
        if not value:
            return
        if not value.isidentifier():
            raise ValidationError('Introduced data is not a valid Python identifier')
