import dataclasses
import importlib
import inspect
import os
import re
import sys
from typing import List, Literal, Optional

import toml
import yaml

from connect.cli.plugins.project.extension.utils import get_event_definitions, get_pypi_runner_version
from connect.eaas.core.extension import Extension
from connect.eaas.core.responses import (
    CustomEventResponse,
    ProcessingResponse,
    ProductActionResponse,
    ValidationResponse,
)


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


def validate_pyproject_toml(config, project_dir, context):
    messages = []
    descriptor_file = os.path.join(project_dir, 'pyproject.toml')
    if not os.path.isfile(descriptor_file):
        messages.append(
            ValidationItem(
                'ERROR',
                (
                    f'The directory *{project_dir}* does not look like an extension project directory, '
                    'the mandatory *pyproject.toml* project descriptor file is not present.'
                ),
                descriptor_file,
            ),
        )
        return ValidationResult(messages, True)
    try:
        data = toml.load(descriptor_file)
    except toml.TomlDecodeError:
        messages.append(
            ValidationItem(
                'ERROR',
                'The extension project descriptor file *pyproject.toml* is not valid.',
                descriptor_file,
            ),
        )
        return ValidationResult(messages, True)

    dependencies = data['tool']['poetry']['dependencies']

    if 'connect-extension-runner' in dependencies:
        messages.append(
            ValidationItem(
                'WARNING',
                'Extensions must depend on *connect-eaas-core* library not *connect-extension-runner*.',
                descriptor_file,
            ),
        )
    elif 'connect-eaas-core' not in dependencies:
        messages.append(
            ValidationItem(
                'ERROR',
                'No dependency on *connect-eaas-core* has been found.',
                descriptor_file,
            ),
        )

    extension_dict = data['tool']['poetry'].get('plugins', {}).get('connect.eaas.ext')
    if not isinstance(extension_dict, dict):
        messages.append(
            ValidationItem(
                'ERROR',
                (
                    'No extension declaration has been found.'
                    'The extension must be declared in the *[tool.poetry.plugins."connect.eaas.ext"]* section.'
                ),
                descriptor_file,
            ),
        )
        return ValidationResult(messages, True)
    if 'extension' not in extension_dict.keys():
        messages.append(
            ValidationItem(
                'ERROR',
                (
                    'Invalid extension declaration in *[tool.poetry.plugins."connect.eaas.ext"]*: '
                    'The extension must be declared as: *"extension" = "your_package.extension:YourExtension"*.'
                ),
                descriptor_file,
            ),
        )
        return ValidationResult(messages, True)

    sys.path.append(os.path.join(os.getcwd(), project_dir))
    package, class_name = extension_dict['extension'].rsplit(':', 1)
    try:
        extension_module = importlib.import_module(package)
    except ImportError as err:
        messages.append(
            ValidationItem(
                'ERROR',
                f'The extension class *{extension_dict["extension"]}* cannot be loaded: {err}.',
                descriptor_file,
            ),
        )
        return ValidationResult(messages, True)

    defined_classes = [
        member[1]
        for member in inspect.getmembers(extension_module, predicate=inspect.isclass)
    ]

    for deprecated_cls, cls_name in (
        (CustomEventResponse, 'InteractiveResponse'),
        (ProcessingResponse, 'BackgroundResponse'),
        (ProductActionResponse, 'InteractiveResponse'),
        (ValidationResponse, 'InteractiveResponse'),
    ):
        if deprecated_cls in defined_classes:
            messages.append(
                ValidationItem(
                    'WARNING',
                    f'The response class *{deprecated_cls.__name__}* has been deprecated in favor of *{cls_name}*.',
                    **get_code_context(extension_module, deprecated_cls.__name__),
                ),
            )

    return ValidationResult(messages, False, {'extension_class': getattr(extension_module, class_name)})


def validate_extension_class(config, project_dir, context):
    messages = []

    extension_class = context['extension_class']
    extension_class_file = inspect.getsourcefile(extension_class)
    extension_json_file = os.path.join(os.path.dirname(extension_class_file), 'extension.json')

    if not issubclass(extension_class, Extension):
        messages.append(
            ValidationItem(
                'ERROR',
                f'The extension class *{extension_class.__name__}* '
                'is not a subclass of *connect.eaas.core.extension.Extension*.',
                extension_class_file,
            ),
        )
        return ValidationResult(messages, True)

    try:
        descriptor = extension_class.get_descriptor()
    except FileNotFoundError:
        messages.append(
            ValidationItem(
                'ERROR',
                'The extension descriptor *extension.json* cannot be loaded.',
                extension_json_file,
            ),
        )
        return ValidationResult(messages, True)

    if 'capabilities' in descriptor:
        messages.append(
            ValidationItem(
                'WARNING',
                'Extension capabilities must be declared using the *connect.eaas.core.decorators.event* decorator.',
                extension_json_file,
            ),
        )
    if 'variables' in descriptor:
        messages.append(
            ValidationItem(
                'WARNING',
                'Extension variables must be declared using the *connect.eaas.core.decorators.variables* decorator.',
                extension_json_file,
            ),
        )
    if 'schedulables' in descriptor:
        messages.append(
            ValidationItem(
                'WARNING',
                'Extension schedulables must be declared using the '
                '*connect.eaas.core.decorators.schedulable* decorator.',
                extension_json_file,
            ),
        )
    return ValidationResult(messages, False)


def validate_events(config, project_dir, context):
    messages = []
    extension_class = context['extension_class']
    definitions = {definition['type']: definition for definition in get_event_definitions(config)}
    events = extension_class.get_events()
    for event in events:
        method = getattr(extension_class, event['method'])
        if event['event_type'] not in definitions:
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'The event type *{event["event_type"]}* is not valid.',
                    **get_code_context(method, '@event'),
                ),
            )
            continue

        if definitions[event['event_type']]['object_statuses']:
            invalid_statuses = set(event['statuses']) - set(definitions[event['event_type']]['object_statuses'])
        else:
            invalid_statuses = set(event['statuses'] or [])
        if invalid_statuses:
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'The status/es *{", ".join(invalid_statuses)}* are invalid '
                    f'for the event *{event["event_type"]}*.',
                    **get_code_context(method, '@event'),
                ),
            )

        signature = inspect.signature(method)
        if len(signature.parameters) != 2:
            sig_str = f'{event["method"]}({", ".join(signature.parameters)})'

            messages.append(
                ValidationItem(
                    'ERROR',
                    f'The handler for the event *{event["event_type"]}* has an invalid signature: "{sig_str}"',
                    **get_code_context(method, sig_str),
                ),
            )
    return ValidationResult(messages, False, context)


def validate_schedulables(config, project_dir, context):
    messages = []
    extension_class = context['extension_class']
    schedulables = extension_class.get_schedulables()
    for schedulable in schedulables:
        method = getattr(extension_class, schedulable['method'])
        signature = inspect.signature(method)
        if len(signature.parameters) != 2:
            sig_str = f'{schedulable["method"]}({", ".join(signature.parameters)})'

            messages.append(
                ValidationItem(
                    'ERROR',
                    f'The schedulable method *{schedulable["method"]}* has an invalid signature: *{sig_str}*',
                    **get_code_context(method, sig_str),
                ),
            )
    return ValidationResult(messages, False, context)


def validate_variables(config, project_dir, context):  # noqa: CCR001

    messages = []
    extension_class = context['extension_class']
    variables = extension_class.get_variables()
    variable_name_pattern = r'^[A-Za-z](?:[A-Za-z0-9_\-.]+)*$'
    variable_name_regex = re.compile(variable_name_pattern)

    names = []

    for variable in variables:
        if 'name' not in variable:
            messages.append(
                ValidationItem(
                    'ERROR',
                    'Invalid variable declaration: the *name* attribute is mandatory.',
                    **get_code_context(extension_class, '@variables'),
                ),
            )
            continue

        if variable["name"] in names:
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'Duplicate variable name: the variable with name *{variable["name"]}* '
                    'has already been declared.',
                    **get_code_context(extension_class, '@variables'),
                ),
            )

        names.append(variable["name"])

        if not variable_name_regex.match(variable['name']):
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'Invalid variable name: the value *{variable["name"]}* '
                    f'does not match the pattern *{variable_name_pattern}*.',
                    **get_code_context(extension_class, '@variables'),
                ),
            )
        if 'initial_value' in variable and not isinstance(variable['initial_value'], str):
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'Invalid *initial_value* attribute for variable *{variable["name"]}*: '
                    f'must be a non-null string not *{type(variable["initial_value"])}*.',
                    **get_code_context(extension_class, '@variables'),
                ),
            )

        if 'secure' in variable and not isinstance(variable['secure'], bool):
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'Invalid *secure* attribute for variable *{variable["name"]}*: '
                    f'must be a boolean not *{type(variable["secure"])}*.',
                    **get_code_context(extension_class, '@variables'),
                ),
            )

    return ValidationResult(messages, False, context)


def validate_docker_compose_yml(config, project_dir, context):
    messages = []
    compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if not os.path.isfile(compose_file):
        messages.append(
            ValidationItem(
                'WARNING',
                (
                    f'The directory *{project_dir}* does not look like an extension project directory, '
                    'the file *docker-compose.yml* is not present.'
                ),
                compose_file,
            ),
        )
        return ValidationResult(messages, False)
    try:
        data = yaml.safe_load(open(compose_file, 'r'))
    except yaml.YAMLError:
        messages.append(
            ValidationItem(
                'ERROR',
                'The file *docker-compose.yml* is not valid.',
                compose_file,
            ),
        )
        return ValidationResult(messages, False)

    runner_image = f'cloudblueconnect/connect-extension-runner:{get_pypi_runner_version()}'

    for service in data['services']:
        image = data['services'][service].get('image')
        if image != runner_image:
            messages.append(
                ValidationItem(
                    'ERROR',
                    f'Invalid image for service *{service}*: expected *{runner_image}* got *{image}*.',
                    compose_file,
                ),
            )
    return ValidationResult(messages, False)


validators = [
    validate_pyproject_toml,
    validate_docker_compose_yml,
    validate_extension_class,
    validate_events,
    validate_variables,
    validate_schedulables,
]
