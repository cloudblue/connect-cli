import dataclasses
import os
import inspect
from typing import List, Literal, Optional

from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import Validator
import toml


class PythonIdentifierValidator(Validator):

    def validate(self, value, context=None):
        if not value:
            return
        if not value.isidentifier():
            raise ValidationError('Introduced data is not a valid Python identifier')


@dataclasses.dataclass
class ValidationItem:
    level: Literal['WARNING', 'ERROR']
    message: str
    file: Optional[str] = None
    start_line: Optional[int] = None
    lineno: Optional[int] = None
    code: Optional[str] = None


@dataclasses.dataclass
class ValidationResult:
    items: List[ValidationItem]
    must_exit: bool = False
    context: Optional[dict] = None


def get_code_context(obj, pattern):
    source_lines = inspect.getsourcelines(obj)
    file = inspect.getsourcefile(obj)
    start_line = source_lines[1]
    lineno = source_lines[1]
    code = ''.join(source_lines[0])

    for idx, line in enumerate(source_lines[0]):  # pragma: no branchs
        if pattern in line:
            lineno += idx
            break

    if inspect.ismodule(obj):
        code = ''.join(code.splitlines(keepends=True)[0:lineno + 3])

    return {
        'file': file,
        'start_line': start_line,
        'lineno': lineno,
        'code': code,
    }


def load_project_toml_file(path):
    descriptor_file = os.path.join(path, 'pyproject.toml')
    if not os.path.isfile(descriptor_file):
        return ValidationResult(
            items=[
                ValidationItem(
                    'ERROR',
                    (
                        f'The mandatory *pyproject.toml* project descriptor file is not present in the folder {path}.'
                    ),
                    descriptor_file,
                ),
            ],
            must_exit=True,
        )
    try:
        return toml.load(descriptor_file)
    except toml.TomlDecodeError:
        return ValidationResult(
            items=[
                ValidationItem(
                    'ERROR',
                    'The project descriptor file *pyproject.toml* is not a valid toml file.',
                    descriptor_file,
                ),
            ],
            must_exit=True,
        )
