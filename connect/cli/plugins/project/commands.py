#  Copyright © 2021 CloudBlue. All rights reserved.

import click

from connect.cli.plugins.project.helpers import (
    bootstrap_project,
    list_projects,
    validate_project,
)

import os


@click.group(name='project', short_help='Manage project definitions.')
def grp_project():
    pass  # pragma: no cover


@grp_project.group(
    name='report',
    short_help='Manage report projects category.',
)
def grp_project_report():
    pass  # pragma: no cover


@grp_project_report.command(
    name='bootstrap',
    short_help='Bootstrap new report project.',
)
@click.option(
    '--data-dir', '-d',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=True,
    help='Directory where the report project will be created.',
)
def cmd_bootstrap_report_project(data_dir):
    bootstrap_project(data_dir)


@grp_project_report.command(
    name='list',
    short_help='List report projects.',
)
@click.option(
    '--data-dir', '-d',
    default=os.getcwd(),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Working directory for report projects.',
)
def cmd_list_report_project(data_dir):
    list_projects(data_dir)


@grp_project_report.command(
    name='validate',
    short_help='Validate given report project.',
)
@click.option(
    '--project-dir', '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory',
)
def cmd_validate_project(project_dir):
    validate_project(project_dir)


def get_group():
    return grp_project
