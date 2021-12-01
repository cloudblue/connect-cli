#  Copyright © 2021 CloudBlue. All rights reserved.

import os

import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.plugins.project.extension.helpers import (
    bootstrap_extension_project,
    bump_runner_extension_project,
    validate_extension_project,
)
from connect.cli.plugins.project.report.helpers import (
    add_report,
    bootstrap_report_project,
    validate_report_project,
)


@group(name='project', short_help='Manage project definitions.')
def grp_project():
    pass  # pragma: no cover


# REPORTS
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
    bootstrap_report_project(output_dir)


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
def cmd_validate_report_project(project_dir):
    validate_report_project(project_dir)


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


# EXTENSION AS A SERVICE
@grp_project.group(
    name='extension',
    short_help='Manage extension projects.',
)
def grp_project_extension():
    pass  # pragma: no cover


@grp_project_extension.command(
    name='bootstrap',
    short_help='Bootstrap new extension project.',
)
@click.option(
    '--output-dir', '-o',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=False,
    help='Directory where the new extension project will be created.',
)
@pass_config
def cmd_bootstrap_extension_project(config, output_dir):
    bootstrap_extension_project(config, output_dir)


@grp_project_extension.command(
    name='validate',
    short_help='Validate given extension project.',
)
@click.option(
    '--project-dir', '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
def cmd_validate_extension_project(project_dir):
    validate_extension_project(project_dir)


@grp_project_extension.command(
    name='bump',
    short_help='Update runner version to the latest one.',
)
@click.option(
    '--project-dir', '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
def cmd_bump_extension_project(project_dir):
    bump_runner_extension_project(project_dir)


def get_group():
    return grp_project
