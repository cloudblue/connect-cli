import json
import os
from datetime import datetime

import click
from click import ClickException

from cnct import ConnectClient

from cnctcli.actions.reports import execute_report
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
    default=os.getcwd(),
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
    descriptor = os.path.join(
        reports_dir,
        'reports.json',
    )
    if not os.path.exists(descriptor):
        raise ClickException(f'The directory {reports_dir} is not a report project root directory.')

    reports = json.load(open(descriptor, 'r'))

    current_report = None
    for report in reports['reports']:
        if report.get('id') == report_id:
            current_report = report
            break

    if not current_report:
        raise ClickException(f'No report with id {report_id} has been found.')

    client = ConnectClient(
        config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
    )
    execute_report(client, reports_dir, report, output_file)
