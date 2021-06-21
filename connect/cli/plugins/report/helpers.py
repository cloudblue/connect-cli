import json
import os
from datetime import datetime

import click
import pytz
from click import ClickException
from cmr import render

from connect.cli.core.http import get_user_agent
from connect.cli.plugins.report.constants import AVAILABLE_RENDERERS, AVAILABLE_REPORTS
from connect.cli.plugins.report.utils import (
    get_renderer_by_id,
    get_report_by_id,
    get_report_entrypoint,
    handle_report_exception,
    Progress,
)
from connect.cli.plugins.report.wizard import get_report_inputs
from connect.client import ConnectClient, RequestLogger
from connect.reports.constants import CLI_ENV
from connect.reports.datamodels import Account, Report
from connect.reports.parser import parse
from connect.reports.renderers import get_renderer
from connect.reports.validator import validate, validate_with_schema


def load_repo(repo_dir):
    cfg = os.path.join(repo_dir, 'reports.json')
    if not os.path.isfile(cfg):
        raise ClickException(
            f'The directory `{repo_dir}` is not a reports project root directory.',
        )
    try:
        descriptor = json.load(open(cfg, 'r'))
    except json.JSONDecodeError:
        raise ClickException(
            'The reports project descriptor `reports.json` is not a valid json file.',
        )

    errors = validate_with_schema(descriptor)
    if errors:
        raise ClickException(f'Invalid `reports.json`: {errors}')

    repo = parse(repo_dir, descriptor)

    errors = validate(repo)
    if errors:
        raise ClickException(f'Invalid `reports.json`: {",".join(errors)}')

    return repo


def list_reports(repo_dir):
    repo = load_repo(repo_dir)
    repo_info = [
        f'# {repo.name} version {repo.version}\n',
        '---\n\n',
        repo.description,
        '\n\n---\n\n',
    ]
    if repo.reports:
        repo_info.append(AVAILABLE_REPORTS)
        for report in repo.reports:
            repo_info.append(f'| {report.local_id} | {report.name} |\n')

    click.echo(render(''.join(repo_info)))


def show_report_info(repo_dir, local_id):
    repo = load_repo(repo_dir)
    report = get_report_by_id(repo, local_id)
    report_info = [
        f'# {report.name} (ID: {report.local_id})\n',
        '---\n\n',
        report.description,
        '\n\n---\n\n',
        AVAILABLE_RENDERERS,

    ]
    for renderer in report.renderers:
        default = ' '
        if renderer.id == report.default_renderer:
            default = '\u2713'
        report_info.append(
            f'| {renderer.id} | {renderer.description} | {default} |\n')
    click.echo(render(''.join(report_info)))


def execute_report(config, reports_dir, report_id, output_file, output_format):
    repo = load_repo(reports_dir)
    report = get_report_by_id(repo, report_id)

    if config.active.id.startswith('VA') and 'vendor' not in report.audience:
        raise ClickException(
            "This report is not expected to be executed on vendor accounts",
        )

    if config.active.id.startswith('PA') and 'provider' not in report.audience:
        raise ClickException(
            "This report is not expected to be executed on provider accounts",
        )

    entrypoint = get_report_entrypoint(report)

    client = ConnectClient(
        config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        default_limit=500,
        max_retries=3,
        default_headers=get_user_agent(),
        logger=RequestLogger() if config.verbose else None,
    )

    inputs = get_report_inputs(config, client, report.get_parameters())

    click.echo(f'Preparing to run report {report_id}. Please wait...\n')

    progress = Progress(report.name)

    renderer_def = get_renderer_by_id(report, output_format or report.default_renderer)

    renderer = get_renderer(
        renderer_def.type,
        CLI_ENV,
        reports_dir,
        Account(config.active.id, config.active.name),
        Report(report.local_id, report.name, report.description, inputs),
        renderer_def.template,
        renderer_def.args,
    )

    try:
        args = [client, inputs, progress]
        if report.report_spec == '2':
            args.extend(
                [
                    renderer_def.type,
                    renderer.set_extra_context,
                ],
            )
        data = entrypoint(*args)

        out = renderer.render(data, output_file, start_time=datetime.now(tz=pytz.utc))
    except Exception:
        handle_report_exception()
        return
    finally:
        progress.close()

    click.echo(f'\nReport has been completed and saved as {out}\n')
