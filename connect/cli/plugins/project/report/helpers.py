#  Copyright © 2022 CloudBlue. All rights reserved.

import json
import os
import functools

from click import ClickException
from interrogatio.core.dialog import dialogus
from openpyxl import Workbook

from connect.cli import get_version
from connect.cli.core.terminal import console
from connect.cli.plugins.project.report.wizard import (
    ADD_REPORT_QUESTIONS,
    BOOTSTRAP_QUESTIONS,
    BOOTSTRAP_SUMMARY,
    REPORT_ADD_WIZARD_INTRO,
    REPORT_BOOTSTRAP_WIZARD_INTRO,
    REPORT_SUMMARY,
)
from connect.cli.plugins.project.utils import show_validation_result_table
from connect.cli.plugins.project.report.validations import validate_reports_json, validators
from connect.cli.plugins.project.renderer import BoilerplateRenderer


def bootstrap_report_project(output_dir, overwrite):
    console.secho('Bootstraping report project...\n', fg='blue')

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

    project_dir = os.path.join(output_dir, answers['project_slug'])
    if not overwrite and os.path.exists(project_dir):
        raise ClickException(f'The destination directory {project_dir} already exists.')

    exclude = []

    if answers['use_github_actions'] == 'n':
        exclude.extend(['.github', '.github/**/*'])

    answers['cli_version'] = get_version()
    renderer = BoilerplateRenderer(
        context=answers,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates', 'bootstrap'),
        output_dir=project_dir,
        overwrite=overwrite,
        exclude=exclude,
        post_render=functools.partial(
            generate_empty_xlsx,
            os.path.join(
                answers['project_slug'],
                answers['package_name'],
                answers['initial_report_slug'],
            ),
        ),
    )
    renderer.render()

    console.markdown(open(f'{project_dir}/HOWTO.md', 'r').read())


def add_report(project_dir, package_name):
    project_path = os.path.join(project_dir, package_name)
    if not os.path.exists(project_path):
        raise ClickException(
            f'The directory package called `{project_path}` does not exist,'
            '\nPlease, create it or choose an existing one using `-n` option.',
        )

    # Required: check if the project descriptor is valid
    validation_result = validate_reports_json(project_dir, None)
    if validation_result.items:
        errors = [error.message for error in validation_result.items]
        raise ClickException(f'Invalid `reports.json`: {errors}')

    console.secho(f'Adding new report to project {project_dir}...\n', fg='blue')

    answers = dialogus(
        ADD_REPORT_QUESTIONS,
        'Reports add project',
        intro=REPORT_ADD_WIZARD_INTRO,
        summary=REPORT_SUMMARY,
        finish_text='Create',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    report_path = os.path.join(project_path, answers['initial_report_slug'])
    if os.path.exists(report_path):
        raise ClickException(
            f'\nThe report directory called `{report_path}` already exists, '
            '\nplease, choose other report name or delete the existing one.',
        )

    template_folder = os.path.join(os.path.dirname(__file__), 'templates', 'add')
    renderer = BoilerplateRenderer(
        context=answers,
        template_folder=template_folder,
        output_dir=project_path,
        post_render=functools.partial(
            generate_empty_xlsx,
            answers['initial_report_slug'],
        ),
    )
    renderer.render()

    _add_report_to_descriptor(
        project_dir=project_dir,
        package_dir=package_name,
        context=renderer.context,
    )

    console.secho(
        f'\nReport {answers["initial_report_slug"]} has been successfully added to the project'
        f' {project_dir}.',
        fg='blue',
    )


def _add_report_to_descriptor(project_dir, package_dir, context):
    project_descriptor = os.path.join(project_dir, 'reports.json')
    project_desc = json.load(open(project_descriptor, 'r'))

    report = {
        'name': context['initial_report_name'],
        'readme_file': os.path.join(package_dir, context['initial_report_slug'], 'README.md'),
        'entrypoint': f"{package_dir}.{context['initial_report_slug']}.entrypoint.generate",
        'audience': [
            'provider',
            'vendor',
        ],
        'report_spec': '2',
        'parameters': [],
        'renderers': [
            {
                'id': 'xlsx',
                'type': 'xlsx',
                'default': True if context['initial_report_renderer'] == 'xlsx' else False,
                'description': 'Export data in Microsoft Excel 2020 format.',
                'template': os.path.join(
                    package_dir,
                    context['initial_report_slug'],
                    'templates',
                    'xlsx',
                    'template.xlsx',
                ),
                'args': {
                    'start_row': 2,
                    'start_col': 1,
                },
            },
            {
                'id': 'json',
                'type': 'json',
                'default': True if context['initial_report_renderer'] == 'json' else False,
                'description': 'Export data as JSON',
            },
            {
                'id': 'csv',
                'type': 'csv',
                'default': True if context['initial_report_renderer'] == 'csv' else False,
                'description': 'Export data as CSV',
            },
            {
                'id': 'xml',
                'type': 'jinja2',
                'default': True if context['initial_report_renderer'] == 'xml' else False,
                'description': 'Export data as XML',
                'template': os.path.join(
                    package_dir,
                    context['initial_report_slug'],
                    'templates',
                    'xml',
                    'template.xml.j2',
                ),
            },
            {
                'id': 'pdf-portrait',
                'type': 'pdf',
                'default': True if context['initial_report_renderer'] == 'pdf' else False,
                'description': 'Export data as PDF (portrait)',
                'template': os.path.join(
                    package_dir,
                    context['initial_report_slug'],
                    'templates',
                    'pdf',
                    'template.html.j2',
                ),
                'args': {
                    'css_file': os.path.join(
                        package_dir,
                        context['initial_report_slug'],
                        'templates',
                        'pdf',
                        'template.css',
                    ),
                },
            },
        ],
    }
    project_desc['reports'].append(report)

    json.dump(
        project_desc,
        open(f'{project_dir}/reports.json', 'w'),
        indent=4,
    )


def generate_empty_xlsx(dest_dir, base_dir, context):
    destination = os.path.join(
        base_dir,
        dest_dir,
        'templates',
        'xlsx',
    )
    os.makedirs(destination, exist_ok=True)
    wb = Workbook(
        write_only=True,
    )
    wb.create_sheet('Data')
    file_path = os.path.join(
        destination,
        'template.xlsx',
    )
    wb.save(
        file_path,
    )
    console.print(f'File {file_path} generated [bold green]\u2713[/bold green]')


def validate_report_project(project_dir):  # noqa: CCR001
    console.secho(f'Validating project {project_dir}...\n', fg='blue')

    context = {}

    validation_items = []

    for validator in validators:
        result = validator(project_dir, context)
        validation_items.extend(result.items)
        if result.must_exit:
            break
        if result.context:
            context.update(result.context)

    if validation_items:
        console.markdown('# Report validation results')
        show_validation_result_table(validation_items)
        console.secho(
            f'Warning/errors have been found while validating the Report Project {project_dir}.',
            fg='yellow',
        )
    else:
        console.secho(f'Report Project {project_dir} has been successfully validated.', fg='green')
