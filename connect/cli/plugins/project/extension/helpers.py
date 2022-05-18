import collections
import os

import click
import yaml
from click.exceptions import ClickException
from interrogatio.core.dialog import dialogus
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax

from connect.cli.plugins.project.extension.renderer import BoilerplateRenderer
from connect.cli.plugins.project.extension.utils import get_event_definitions, get_pypi_runner_version
from connect.cli.plugins.project.extension.validations import validators
from connect.cli.plugins.project.extension.wizard import (
    EXTENSION_BOOTSTRAP_WIZARD_INTRO,
    get_questions,
    get_summary,
)
from connect.utils.terminal.markdown import render
from connect.utils.terminal.markdown.theme import ConnectTheme


def bootstrap_extension_project(config, data_dir, overwrite):
    click.secho('Bootstraping extension project...\n', fg='blue')

    answers = None
    statuses_by_event = {}

    definitions = get_event_definitions(config)
    grouped_definitions = collections.defaultdict(lambda: collections.defaultdict(list))

    for elem in definitions:
        statuses_by_event[elem['type']] = elem['object_statuses']
        grouped_definitions[elem['category']][elem['group']].append(elem)

    answers = dialogus(
        get_questions(config, grouped_definitions),
        'Extension project bootstrap',
        intro=EXTENSION_BOOTSTRAP_WIZARD_INTRO,
        summary=get_summary(config, grouped_definitions),
        finish_text='Create',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    ctx = {
        'statuses_by_event': statuses_by_event,
        'background': {},
        'interactive': {},
        'runner_version': get_pypi_runner_version(),
    }

    for var, answer in answers.items():
        if var.startswith('background_'):
            ctx['background'].update({var: answer})
        elif var.startswith('interactive_'):
            ctx['interactive'].update({var: answer})
        else:
            ctx.update({var: answer})

    renderer = BoilerplateRenderer(data_dir, ctx, overwrite)
    project_dir = renderer.render()

    click.echo(render(open(f'{project_dir}/HOWTO.md', 'r').read()))


def validate_extension_project(config, project_dir):  # noqa: CCR001
    click.secho(f'Validating project {project_dir}...\n', fg='blue')

    context = {}

    validation_items = []

    for validator in validators:
        result = validator(config, project_dir, context)
        validation_items.extend(result.items)
        if result.must_exit:
            break
        if result.context:
            context.update(result.context)

    console = Console(theme=ConnectTheme())
    if validation_items:
        click.echo(render('# Extension validation results'))
        for item in validation_items:
            table = Table(
                box=box.ROUNDED,
                show_header=False,
            )
            table.add_column('Field', style='blue')
            table.add_column('Value')
            level_color = 'red' if item.level == 'ERROR' else 'yellow'
            table.add_row('Level', f'[bold {level_color}]{item.level}[/]')
            table.add_row('Message', Markdown(item.message))
            table.add_row('File', item.file or '-')
            table.add_row(
                'Code',
                Syntax(
                    item.code,
                    'python3',
                    theme='ansi_light',
                    dedent=True,
                    line_numbers=True,
                    start_line=item.start_line,
                    highlight_lines={item.lineno},
                ) if item.code else '-',
            )
            console.print(table)
        click.secho(
            f'Warning/errors have been found while validating the Extension Project {project_dir}.',
            fg='yellow',
        )
    else:
        click.secho(f'Extension Project {project_dir} has been successfully validated.', fg='green')


def bump_runner_extension_project(project_dir: str):
    click.secho(f'Bumping runner version on project {project_dir}...\n', fg='blue')

    latest_version = get_pypi_runner_version()
    docker_compose_file = os.path.join(project_dir, 'docker-compose.yml')
    if not os.path.isfile(docker_compose_file):
        raise ClickException(f'Mandatory `docker-compose.yml` file on directory `{project_dir}` is missing.')
    try:
        with open(docker_compose_file, 'r') as file_reader:
            data = yaml.load(file_reader, Loader=yaml.FullLoader)
            for service in data['services']:
                if 'image' in data['services'][service]:
                    runner_image = data['services'][service]['image']
                    runner_version = runner_image.split(':')[-1]
                    updated_image = runner_image.replace(runner_version, latest_version)
                    data['services'][service]['image'] = updated_image
        with open(docker_compose_file, 'w') as file_writer:
            yaml.dump(data, file_writer, sort_keys=False)
    except yaml.YAMLError as error:
        raise ClickException(
            '`docker_compose.yml` file is not properly formatted. Please review it.\n'
            f'Error: {error}',
        )

    click.secho(f'Runner version has been successfully updated to {latest_version}', fg='green')
