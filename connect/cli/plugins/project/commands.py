#  Copyright © 2022 CloudBlue. All rights reserved.

import os

import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.plugins.project.extension.helpers import (
    bootstrap_extension_project,
    bump_runner_extension_project,
    deploy_extension_project,
    validate_extension_project,
)
from connect.cli.plugins.project.report.helpers import (
    add_report,
    bootstrap_report_project,
    validate_report_project,
)


class Mutex(click.Option):
    def __init__(self, *args, **kwargs):
        self.conflict_with: list = kwargs.pop('conflict_with')

        assert self.conflict_with, "'conflict_with' parameter required"

        help_str = kwargs.get('help', '')
        help_str += f' This option is mutually exclusive with {", ".join(self.conflict_with)}.'
        kwargs['help'] = help_str.strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt: bool = self.name in opts
        for mutex_opt in self.conflict_with:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError(
                        f'Illegal usage: options {self.name} and {mutex_opt} are mutually exclusive.',
                    )
                else:
                    self.prompt = None
        return super(Mutex, self).handle_parse_result(ctx, opts, args)


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
    '--output-dir',
    '-o',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=True,
    help='Directory where the new report project will be created.',
)
@click.option(
    '--force-overwrite',
    '-f',
    is_flag=True,
    help='Overwrite the destination project directory if exists.',
    default=False,
)
def cmd_bootstrap_report_project(output_dir, force_overwrite):
    bootstrap_report_project(output_dir, force_overwrite)


@grp_project_report.command(
    name='validate',
    short_help='Validate given report project.',
)
@click.option(
    '--project-dir',
    '-p',
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
    '--project-dir',
    '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
@click.option(
    '--package-name',
    '-n',
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
    '--output-dir',
    '-o',
    default=os.getcwd(),
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=False,
    help='Directory where the new extension project will be created.',
)
@click.option(
    '--force-overwrite',
    '-f',
    is_flag=True,
    help='Overwrite the destination project directory if exists.',
    default=False,
)
@click.option(
    '--save-answers',
    '-s',
    default=None,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    required=False,
    help='Path to JSON file where to save wizard answers.',
    cls=Mutex,
    conflict_with=['load_answers'],
)
@click.option(
    '--load-answers',
    '-l',
    default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=False,
    help='Path to JSON file from where load wizard answers.',
    cls=Mutex,
    conflict_with=['save_answers'],
)
@pass_config
def cmd_bootstrap_extension_project(
    config,
    output_dir,
    force_overwrite,
    save_answers,
    load_answers,
):
    bootstrap_extension_project(
        config,
        output_dir,
        force_overwrite,
        save_answers,
        load_answers,
    )


@grp_project_extension.command(
    name='validate',
    short_help='Validate given extension project.',
)
@click.argument(
    'project_dir',
    metavar='PROJECT_DIR',
    nargs=1,
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@pass_config
def cmd_validate_extension_project(config, project_dir):
    validate_extension_project(config, project_dir)


@grp_project_extension.command(
    name='bump',
    short_help='Update runner version to the latest one.',
)
@click.option(
    '--project-dir',
    '-p',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Project directory.',
)
def cmd_bump_extension_project(project_dir):
    bump_runner_extension_project(project_dir)


@grp_project_extension.command(
    name='deploy',
    short_help='Deploy extension.',
)
@click.argument('repo', metavar='repo', nargs=1, required=True)
@click.option(
    '--tag',
    '-t',
    required=False,
    default=None,
    type=str,
    help='Repository tag.',
)
@pass_config
def cmd_deploy_extension(config, repo, tag):
    deploy_extension_project(config, repo, tag)


def get_group():
    return grp_project
