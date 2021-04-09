#  Copyright © 2021 CloudBlue. All rights reserved.

import os

import click

from connect.cli.plugins.project.helpers import (
    add_report,
    bootstrap_project,
    validate_project,
)


@click.group(name='project', short_help='Manage project definitions.')
def grp_project():
    pass  # pragma: no cover


@grp_project.group(
    name='report',
    short_help='Manage report projects.',
)
def grp_project_report():
    pass  # pragma: no cover


@grp_project_report.command(
    name='bootstrap',
    short_help='Bootstrap new report project.',
)
@click.option(
    '--output-dir', '-o',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=True,
    help='Directory where the new report project will be created.',
)
def cmd_bootstrap_report_project(output_dir):
    bootstrap_project(output_dir)


@grp_project_report.command(
    name='validate',
    short_help='Validate given report project.',
)
@click.option(
    '--project-dir', '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
def cmd_validate_project(project_dir):
    validate_project(project_dir)


@grp_project_report.command(
    name='add',
    short_help='Add new report to the given project.',
)
@click.option(
    '--project-dir', '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
@click.option(
    '--package-name', '-n',
    default='reports',
    help='Package directory.',
)
def cmd_add_report(project_dir, package_name):
    add_report(project_dir, package_name)


def get_group():
    return grp_project
