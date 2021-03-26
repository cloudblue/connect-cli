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

from cmr import render

import click
from click import ClickException

from connect.reports.datamodels import RepositoryDefinition


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
