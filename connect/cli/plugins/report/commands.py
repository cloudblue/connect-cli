import os
from datetime import datetime

import click

from connect.cli.core.config import pass_config
from connect.cli.plugins.report.helpers import (
    execute_report,
    list_reports,
    show_report_info,
)


DEFAULT_REPORT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '../../../.data/connect_reports'),
)


@click.group(name='report', short_help='Reports execution and development.')
def grp_report():
    pass  # pragma: no cover


@grp_report.command(
    name='execute',
    short_help='Execute a report.',
)
@click.argument('report_id', metavar='REPORT_ID', nargs=1, required=True)
@click.option(
    '--reports-dir',
    '-d',
    'reports_dir',
    default=DEFAULT_REPORT_DIR,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Report project root directory.',
)
@click.option(
    '--output-file',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output file.',
)
@click.option(
    '--output-format',
    '-f',
    'output_format',
    help='Output format.',
)
@pass_config
def cmd_execute_report(config, reports_dir, report_id, output_file, output_format):
    if not output_file:
        output_file = os.path.join(
            os.getcwd(),
            f'report_{report_id}_{datetime.now().strftime("%Y%m%d_%H%M")}',
        )
    execute_report(config, reports_dir, report_id, output_file, output_format)


@grp_report.command(
    name='list',
    short_help='List available reports.',
)
@click.option(
    '--reports-dir',
    '-d',
    'reports_dir',
    default=DEFAULT_REPORT_DIR,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Report project root directory. Do not specify for listing default reports.',
)
def cmd_list_reports(reports_dir):
    list_reports(reports_dir)


@grp_report.command(
    name='info',
    short_help='Get additional information for a given report.',
)
@click.argument('report_id', metavar='REPORT_ID', nargs=1, required=True)
@click.option(
    '--reports-dir',
    '-d',
    'reports_dir',
    default=DEFAULT_REPORT_DIR,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Report project root directory. Do not specify for listing default reports',
)
def get_report_info(reports_dir, report_id):
    show_report_info(reports_dir, report_id)


def get_group():
    return grp_report
