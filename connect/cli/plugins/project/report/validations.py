
#  Copyright © 2022 CloudBlue. All rights reserved.

import json
import os
import sys
import inspect
import importlib

from poetry.core.constraints.version import parse_constraint, Version

from connect.reports.parser import parse
from connect.reports.validator import (
    validate,
    validate_with_schema,
)
from connect.cli.plugins.project.validators import (
    get_code_context,
    load_project_toml_file,
    ValidationItem,
    ValidationResult,
)
from connect.cli.core.utils import get_last_cli_version


def validate_pyproject_toml(project_dir, context):
    messages = []
    data = load_project_toml_file(project_dir)
    if isinstance(data, ValidationResult):
        return data

    descriptor_file = os.path.join(project_dir, 'pyproject.toml')
    dependencies = data.get('tool', {}).get('poetry', {}).get('dev-dependencies', {})

    if not dependencies or 'connect-cli' not in dependencies:
        messages.append(
            ValidationItem(
                'WARNING',
                'No development dependency on *connect-cli* has been found.',
                descriptor_file,
            ),
        )
    if 'connect-cli' in dependencies:
        project_version = parse_constraint(dependencies['connect-cli'])
        last_version = get_last_cli_version()
        if not last_version:
            messages.append(
                ValidationItem(
                    'WARNING',
                    f'The version {dependencies["connect-cli"]} specified in your '
                    'pyproject.toml cannot be verified to include the lastest connect-cli.',
                    descriptor_file,
                ),
            )
        else:
            major, minor = last_version.split('.')
            last_version_obj = Version.from_parts(int(major), int(minor))
            if not project_version.allows(last_version_obj):
                messages.append(
                    ValidationItem(
                        'WARNING',
                        f'The version range {dependencies["connect-cli"]} specified in your '
                        'pyproject.toml does not include the lastest connect-cli version which is '
                        f'{last_version}.',
                        descriptor_file,
                    ),
                )

    return ValidationResult(messages, False)


def validate_reports_json(project_dir, context):
    messages = []
    descriptor_file = os.path.join(project_dir, 'reports.json')
    if not os.path.isfile(descriptor_file):
        messages.append(
            ValidationItem(
                'ERROR',
                f'The directory `{project_dir}` does not look like a report project directory,'
                ' the mandatory `reports.json` file descriptor is not present.',
            ),
        )
    else:
        try:
            _load_reports_json(project_dir)
        except json.JSONDecodeError:
            messages.append(
                ValidationItem(
                    'ERROR',
                    'The report project descriptor `reports.json` is not a valid json file.',
                ),
            )
    return ValidationResult(messages, True if messages else False)


def validate_report_json_with_schema(project_dir, context):
    messages = []
    project_desc = _load_reports_json(project_dir)
    errors = validate_with_schema(project_desc)
    if errors:
        messages.append(
            ValidationItem(
                level='ERROR',
                message=errors,
            ),
        )
    return ValidationResult(messages, True if messages else False)


def validate_repository_definition(project_dir, context):
    messages = []
    data = _load_reports_json(project_dir)
    report_project = parse(project_dir, data)
    errors = validate(report_project)
    if errors:
        for error in errors:
            messages.append(
                ValidationItem(
                    level='ERROR',
                    message=error,
                ),
            )
    else:
        for report in report_project.reports:
            error = _validate_entrypoint(
                project_dir,
                report.entrypoint,
                report.report_spec,
            )
            if error:
                messages.append(error)
    return ValidationResult(messages, True if messages else False)


def _load_reports_json(project_dir):
    descriptor_file = os.path.join(project_dir, 'reports.json')
    with open(descriptor_file, 'r') as f:
        return json.load(f)


def _validate_entrypoint(project_dir, entrypoint, report_spec):
    sys.path.append(project_dir)
    package = entrypoint.rsplit('.', 1)[0]
    try:
        entrypoint_module = importlib.import_module(package)
    except ImportError as error:
        return ValidationItem(
            'ERROR',
            f'\nErrors detected on entrypoint module: {error}',
        )
    # Function validation
    if report_spec == '1' and len(inspect.signature(entrypoint_module.generate).parameters) != 3:
        return ValidationItem(
            'ERROR',
            'Wrong arguments on `generate` function. The signature must be:'
            '\n`def generate(client, parameters, progress_callback)`',
            **get_code_context(entrypoint_module.generate, 'def generate'),
        )
    if report_spec == '2' and len(inspect.signature(entrypoint_module.generate).parameters) != 5:
        return ValidationItem(
            'ERROR',
            'Wrong arguments on `generate` function. The signature must be:'
            '\n`def generate(client=None, input_data=None, progress_callback=None, '
            'renderer_type=None, extra_context_callback=None)`',
            **get_code_context(entrypoint_module.generate, 'def generate'),
        )


validators = [
    validate_pyproject_toml,
    validate_reports_json,
    validate_report_json_with_schema,
    validate_repository_definition,
]
