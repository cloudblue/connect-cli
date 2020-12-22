import json
import os
from datetime import datetime

import click
from click import ClickException

from cnctcli.actions.reports import execute_report, validate_report_json
from cnctcli.config import pass_config


@click.group(name='report', short_help='commands related to report management')
def grp_report():
    pass  # pragma: no cover


@grp_report.command(
    name='execute',
    short_help='execute a report',
)
@click.argument('report_id', metavar='REPORT_ID', nargs=1, required=True)
@click.option(
    '--reports-dir',
    '-d',
    'reports_dir',
    default=os.path.join(
        os.getcwd(),
        'cnctcli',
        'reports',
        'connect-reports'
    ),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Report project root directory.'
)
@click.option(
    '--output-file',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output Excel file.'
)
@pass_config
def cmd_execute_report(config, report_id, reports_dir, output_file):
    if not output_file:
        output_file = os.path.join(
            os.getcwd(),
            'report_{report_id}_{report_date}.xlsx'.format(
                report_id=report_id,
                report_date=datetime.now().strftime('%Y%m%d_%H%M'),
            )
        )

    reports = load_reports(reports_dir)

    current_report = None
    for report in reports['reports']:
        if report.get('id') == report_id:
            current_report = report
            break

    if not current_report:
        raise ClickException(f'No report with id {report_id} has been found.')

    execute_report(config, reports_dir, report, output_file)


@grp_report.command(
    name='list',
    short_help='list available reports',
)
@click.option(
    '--reports-dir',
    '-d',
    'reports_dir',
    default=os.path.join(
        os.getcwd(),
        'cnctcli',
        'reports',
        'connect-reports'
    ),
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Report project root directory. Do not specify for listing default reports'
)
def cmd_list_reports(reports_dir):
    reports = load_reports(reports_dir)
    if 'reports' in reports and len(reports["reports"]) > 0:
        click.echo(f'{reports["name"]} version {reports["version"]}')
        click.echo(f'{reports["description"]}')
        click.echo('\n')
        for report in reports["reports"]:
            click.echo(
                click.style(
                    f'ID: {report["id"]} - {report["name"]}',
                    fg='green'
                )
            )
            click.echo(f'\t{report["description"]}')
    else:
        click.echo(
            click.style(
                f'No reports found in {reports_dir}',
                fg='magenta',
            ),
        )


def load_reports(reports_dir):
    descriptor = os.path.join(
        reports_dir,
        'reports.json',
    )
    if not os.path.exists(descriptor):
        raise ClickException(f'The directory {reports_dir} is not a report project root directory.')

    reports = json.load(open(descriptor, 'r'))
    validate_report_json(reports, reports_dir)

    return reports
