#  Copyright © 2021 CloudBlue. All rights reserved.

from cookiecutter.main import cookiecutter
from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.utils import rmtree
from cookiecutter.exceptions import OutputDirExistsException

from connect.cli.plugins.project.constants import (
    AVAILABLE_PROJECTS,
    BOILERPLATE_URL,
)

import glob
import json
import os
import sys
import inspect

from cmr import render

import click
from click import ClickException

from connect.reports.datamodels import RepositoryDefinition
from connect.reports.validator import (
    validate,
    validate_with_schema,
)
from connect.reports.parser import parse


def bootstrap_project(data_dir: str):
    click.secho('Bootstraping report project...\n', fg='blue')

    # Avoid asking rewrite clone boilerplate project
    cookie_dir = DEFAULT_CONFIG['cookiecutters_dir']
    rmtree(cookie_dir)
    try:
        project_dir = cookiecutter(BOILERPLATE_URL, output_dir=data_dir)
        click.secho(f'\nReport Project location: {project_dir}', fg='blue')
    except OutputDirExistsException as error:
        project_path = str(error).split('"')[1]
        raise ClickException(
            f'\nThe directory "{project_path}" is already created, '
            '\nif you would like to use that name, please delete '
            'the directory or use another location.',
        )


def list_projects(data_dir: str):
    project_list = glob.glob(f'{data_dir}/**/reports.json')
    if len(project_list) == 0:
        click.echo(render(AVAILABLE_PROJECTS))
        click.secho('No projects found!', fg='red')
        return
    project_info = []
    project_info.append(AVAILABLE_PROJECTS)
    for project_json in project_list:
        try:
            data = json.load(open(project_json, 'r'))
        except json.JSONDecodeError:
            raise ClickException(
                'The reports project descriptor `reports.json` is not a valid json file.',
            )
        data.pop('reports')
        project = RepositoryDefinition(root_path=data_dir, **data)
        project_info.append(f'| {project.name} | {project.version} |\n')

    click.echo(render(''.join(project_info)))


def validate_project(project_dir):
    click.secho(f'Validating project {project_dir}...\n', fg='blue')

    data = _file_descriptor_validations(project_dir)

    errors = validate_with_schema(data)
    if errors:
        raise ClickException(f'Invalid `reports.json`: {errors}')

    report_project = parse(project_dir, data)

    errors = validate(report_project)
    if errors:
        raise ClickException(f'Invalid `reports.json`: {",".join(errors)}')

    for report in report_project.reports:
        _entrypoint_validations(project_dir, report.entrypoint, report.report_spec)

    click.secho(f'Report Project {project_dir} has been successfully validated.', fg='green')


def _file_descriptor_validations(project_dir):
    descriptor_file = os.path.join(project_dir, 'reports.json')
    if not os.path.isfile(descriptor_file):
        raise ClickException(
            f'The directory `{project_dir}` does not seem a report project directory, '
            'the mandatory `reports.json` file descriptor is not present.',
        )
    try:
        data = json.load(open(descriptor_file, 'r'))
    except json.JSONDecodeError:
        raise ClickException(
            'The report project descriptor `reports.json` is not a valid json file.',
        )
    return data


def _entrypoint_validations(project_dir, entrypoint, report_spec):
    # Package validation
    sys.path.append(os.path.join(os.getcwd(), project_dir))
    package = entrypoint.rsplit('.', 1)[0]
    try:
        entrypoint_module = inspect.importlib.import_module(package)
    except Exception as error:
        raise ClickException(f'\nErrors detected on entrypoint module: {error}')

    # Function validation
    if report_spec == '1' and len(inspect.signature(entrypoint_module.generate).parameters) != 3:
        raise ClickException(
            'Wrong arguments on `generate` function. The signature must be:'
            '\n>> def generate(client, parameters, progress_callback) <<',
        )
    if report_spec == '2' and len(inspect.signature(entrypoint_module.generate).parameters) != 5:
        raise ClickException(
            'Wrong arguments on `generate` function. The signature must be:'
            '\n>> def generate(client=None, input_data=None, progress_callback=None, '
            'renderer_type=None, extra_context_callback=None) <<',
        )
