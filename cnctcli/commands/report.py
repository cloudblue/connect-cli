import json
import os
from datetime import datetime

import click
from click import ClickException

from cnctcli.actions.reports import (
    execute_report,
    validate_report_json,
    get_report_id,
    get_report_description,
)

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
        click.echo(f'{"*" * 60}\n')
        click.echo(f'{reports["name"]} version {reports["version"]}')
        click.echo(f'\n{"*" * 60}\n')
        click.echo(f'{get_report_description(reports_dir, reports["readme_file"])}')
        click.echo(f'{"*" * 60}')
        click.echo('\nList of available reports:\n')
        for report in reports["reports"]:
            click.echo(
                click.style(
                    f'Report ID: {report["id"]} - Report name: {report["name"]}',
                    fg='green',
                )
            )
    else:
        click.echo(
            click.style(
                f'No reports found in {reports_dir}',
                fg='magenta',
            ),
        )


@grp_report.command(
    name='info',
    short_help='Get additional information for a given report',
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
    help='Report project root directory. Do not specify for listing default reports'
)
def get_report_info(report_id, reports_dir):
    reports = load_reports(reports_dir)
    if 'reports' in reports and len(reports["reports"]) > 0:
        report = None
        for rep in reports["reports"]:
            if rep['id'] == report_id:
                report = rep
                break

        if report:
            click.echo(f'{"*" * 60}\n')
            click.echo(
                click.style(
                    f'Report ID: {report["id"]}\nReport name: {report["name"]}\n',
                    fg='green',
                )
            )
            click.echo(f'{"*" * 60}\n')
            click.echo(f'{get_report_description(reports_dir, report["readme_file"])}')
        else:
            click.echo(
                click.style(
                    f'No report with id {report_id}',
                    fg='magenta',
                ),
            )
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

    try:
        reports_descriptor = json.load(open(descriptor, 'r'))
    except json.decoder.JSONDecodeError:
        raise ClickException("Error reading reports.json, invalid JSON format")
    validate_report_json(reports_descriptor, reports_dir)
    reports = []
    for report in reports_descriptor['reports']:
        report['id'] = get_report_id(report['entrypoint'])
        reports.append(report)

    reports_descriptor['reports'] = reports

    return reports_descriptor
