import asyncio
import inspect
import json
import os
from datetime import datetime

import pytz
from click import ClickException

from connect.cli.core.http import get_user_agent, RequestLogger
from connect.cli.core.terminal import console
from connect.cli.core.utils import field_to_check_mark
from connect.cli.plugins.report.constants import AVAILABLE_REPORTS
from connect.cli.plugins.report.utils import (
    get_renderer_by_id,
    get_report_by_id,
    get_report_entrypoint,
    handle_report_exception,
    Progress,
)
from connect.cli.plugins.report.wizard import get_report_inputs
from connect.client import AsyncConnectClient, ConnectClient
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

    console.markdown(''.join(repo_info))


def show_report_info(repo_dir, local_id):
    repo = load_repo(repo_dir)
    report = get_report_by_id(repo, local_id)

    report_info = [
        f'# {report.name} (ID: {report.local_id})\n',
        '---\n\n',
        report.description,
        '\n\n---\n\n',
    ]

    console.markdown(''.join(report_info))

    console.header('Available output formats')

    console.table(
        columns=(
            'ID',
            'Description',
            ('center', 'Default'),
        ),
        rows=[
            (
                renderer.id,
                renderer.description,
                field_to_check_mark(renderer.id == report.default_renderer),
            )
            for renderer in report.renderers
        ],
    )


async def execute_report_async(entrypoint, args, renderer, output_file):
    if inspect.iscoroutinefunction(entrypoint):
        data = await entrypoint(*args)
    else:
        data = entrypoint(*args)
    return await renderer.render_async(
        data,
        output_file,
        start_time=datetime.now(tz=pytz.utc),
    )


def _run_render(is_async, entrypoint, args, renderer, output_file):
    if is_async:
        return asyncio.run(execute_report_async(entrypoint, args, renderer, output_file))
    else:
        data = entrypoint(*args)
        return renderer.render(data, output_file, start_time=datetime.now(tz=pytz.utc))


def execute_report(config, reports_dir, report_id, output_file, output_format):
    repo = load_repo(reports_dir)
    report = get_report_by_id(repo, report_id)

    if config.active.is_vendor() and 'vendor' not in report.audience:
        raise ClickException(
            "This report is not expected to be executed on vendor accounts",
        )

    if config.active.is_provider() and 'provider' not in report.audience:
        raise ClickException(
            "This report is not expected to be executed on provider accounts",
        )

    available_renderers = [r.id for r in report.renderers]

    if output_format and output_format not in available_renderers:
        raise ClickException(
            f'The format {output_format} is not available for report {report_id}',
        )

    entrypoint = get_report_entrypoint(report)

    is_async = inspect.isasyncgenfunction(entrypoint) or inspect.iscoroutinefunction(entrypoint)

    sync_client = ConnectClient(
        config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        default_limit=500,
        max_retries=5,
        default_headers=get_user_agent(),
        logger=RequestLogger(),
        resourceset_append=False,
    )
    if is_async:
        async_client = AsyncConnectClient(
            config.active.api_key,
            endpoint=config.active.endpoint,
            use_specs=False,
            default_limit=500,
            max_retries=5,
            default_headers=get_user_agent(),
            logger=RequestLogger(),
            resourceset_append=False,
        )

    output_format = output_format or report.default_renderer

    inputs = get_report_inputs(config, sync_client, report, output_format)

    console.echo(f'Preparing to run report {report_id}. Please wait...\n')

    progress = Progress(report.name)

    renderer_def = get_renderer_by_id(report, output_format)

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
        args = [async_client if is_async else sync_client, inputs, progress]
        if report.report_spec == '2':
            args.extend(
                [
                    renderer_def.type,
                    renderer.set_extra_context,
                ],
            )
        out = _run_render(is_async, entrypoint, args, renderer, output_file)

    except Exception:
        handle_report_exception()
        return
    finally:
        progress.close()

    console.echo(f'\nReport has been completed and saved as {out}\n')
