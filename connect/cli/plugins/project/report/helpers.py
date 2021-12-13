#  Copyright © 2021 CloudBlue. All rights reserved.

import json
import os
import sys
import inspect
import importlib
import tempfile
import shutil

import click
from click import ClickException
from cookiecutter.main import cookiecutter
from cookiecutter.config import get_user_config
from cookiecutter.exceptions import OutputDirExistsException, RepositoryCloneFailed
from cookiecutter.generate import generate_context, generate_files
from cookiecutter.repository import determine_repo_dir
from interrogatio.core.dialog import dialogus

from connect.cli.plugins.project.cookiehelpers import force_delete, purge_cookiecutters_dir
from connect.cli.plugins.project.git import get_highest_version, GitException
from connect.cli.plugins.project.report.constants import (
    PROJECT_REPORT_BOILERPLATE_TAG,
    PROJECT_REPORT_BOILERPLATE_URL,
)
from connect.cli.plugins.project.report.wizard import (
    ADD_REPORT_QUESTIONS,
    BOOTSTRAP_QUESTIONS,
    BOOTSTRAP_SUMMARY,
    REPORT_ADD_WIZARD_INTRO,
    REPORT_BOOTSTRAP_WIZARD_INTRO,
    REPORT_SUMMARY,
)
from connect.reports.parser import parse
from connect.reports.validator import (
    validate,
    validate_with_schema,
)


def bootstrap_report_project(data_dir: str):
    click.secho('Bootstraping report project...\n', fg='blue')
    purge_cookiecutters_dir()
    answers = dialogus(
        BOOTSTRAP_QUESTIONS,
        'Reports project bootstrap',
        intro=REPORT_BOOTSTRAP_WIZARD_INTRO,
        summary=BOOTSTRAP_SUMMARY,
        finish_text='Create',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    try:
        checkout_tag, _ = PROJECT_REPORT_BOILERPLATE_TAG or get_highest_version(PROJECT_REPORT_BOILERPLATE_URL)

        project_dir = cookiecutter(
            PROJECT_REPORT_BOILERPLATE_URL,
            checkout=checkout_tag,
            no_input=True,
            extra_context=answers,
            output_dir=data_dir,
        )
        click.secho(f'\nReports Project location: {project_dir}', fg='blue')
    except GitException as error:
        raise ClickException(f'\nAn error occured on tags retrieval: {error}')
    except RepositoryCloneFailed as error:
        raise ClickException(f'\nAn error occured while cloning the project: {error}')
    except OutputDirExistsException as error:
        project_path = str(error).split('"')[1]
        raise ClickException(
            f'\nThe directory "{project_path}" already exists, '
            '\nif you would like to use that name, please delete '
            'the directory or use another location.',
        )


def validate_report_project(project_dir):
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


def add_report(project_dir, package_name):
    if not os.path.isdir(f'{project_dir}/{package_name}'):
        raise ClickException(
            f'The directory package called `{package_name}` does not exist,'
            '\nPlease, create it or choose an existing one using `-n` option.',
        )

    # Required: check if the project descriptor is valid
    project_desc = _file_descriptor_validations(project_dir)
    errors = validate_with_schema(project_desc)
    if errors:
        raise ClickException(f'Invalid `reports.json`: {errors}')

    click.secho(f'Adding new report to project {project_dir}...\n', fg='blue')

    with tempfile.TemporaryDirectory() as add_report_tmpdir:

        # Instead of using cookiecutter use the internals
        report_dir, report_slug = _custom_cookiecutter(
            PROJECT_REPORT_BOILERPLATE_URL,
            add_report_tmpdir,
            project_dir,
            package_name,
        )
        if os.path.isdir(f'{project_dir}/{package_name}/{report_slug}'):
            raise ClickException(
                f'\nThe report directory called `{project_dir}/{package_name}/{report_slug}` already exists, '
                '\nplease, choose other report name or delete the existing one.',
            )

        shutil.move(
            f'{report_dir}/{package_name}/{report_slug}',
            f'{project_dir}/{package_name}/',
        )

        _add_report_to_descriptor(project_dir, report_dir, package_name)

        click.secho('\nReport has been successfully created.', fg='blue')


def _custom_cookiecutter(template, output_dir, project_slug, package_slug):

    config_dict = get_user_config(
        config_file=None, default_config=False,
    )

    template_name = os.path.splitext(os.path.basename(template))[0]

    repo_dir = os.path.join(config_dict['cookiecutters_dir'], template_name)
    if os.path.isdir(repo_dir):
        shutil.rmtree(repo_dir, onerror=force_delete)

    repo_dir, _ = determine_repo_dir(
        template=template,
        abbreviations=config_dict['abbreviations'],
        clone_to_dir=config_dict['cookiecutters_dir'],
        checkout=None,
        no_input=False,
        password=None,
        directory=None,
    )

    context_file = os.path.join(repo_dir, 'cookiecutter.json')
    context = generate_context(
        context_file=context_file,
        default_context=config_dict['default_context'],
        extra_context=None,
    )

    answers = dialogus(
        ADD_REPORT_QUESTIONS,
        'Add report to existing project',
        intro=REPORT_ADD_WIZARD_INTRO,
        summary=REPORT_SUMMARY,
        finish_text='Add',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    context['cookiecutter']['_template'] = template
    context['cookiecutter']['project_slug'] = project_slug
    context['cookiecutter']['package_slug'] = package_slug
    context['cookiecutter']['initial_report_name'] = answers['initial_report_name']
    context['cookiecutter']['initial_report_slug'] = answers['initial_report_slug']
    context['cookiecutter']['initial_report_description'] = answers['initial_report_description']
    context['cookiecutter']['initial_report_renderer'] = answers['initial_report_renderer']

    result = _generate_files(context, output_dir, repo_dir)

    return result, context['cookiecutter']['initial_report_slug']


def _generate_files(context, output_dir, repo_dir):
    result = generate_files(
        repo_dir=repo_dir,
        context=context,
        overwrite_if_exists=False,
        skip_if_file_exists=False,
        output_dir=output_dir,
    )
    return result


def _add_report_to_descriptor(project_dir, report_dir, package_slug):
    project_descriptor = os.path.join(project_dir, 'reports.json')
    project_desc = json.load(open(project_descriptor, 'r'))

    temporal_descriptor = os.path.join(report_dir, 'reports.json')
    temporal_desc = json.load(open(temporal_descriptor, 'r'))

    report_dict = temporal_desc['reports'][0]
    project_desc['reports'].append(report_dict)

    json.dump(
        project_desc,
        open(f'{project_dir}/reports.json', 'w'),
        indent=4,
    )


def _file_descriptor_validations(project_dir):
    descriptor_file = os.path.join(project_dir, 'reports.json')
    if not os.path.isfile(descriptor_file):
        raise ClickException(
            f'The directory `{project_dir}` does not look like a report project directory, '
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
        entrypoint_module = importlib.import_module(package)
    except ImportError as error:
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
