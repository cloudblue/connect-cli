# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.

import click
from connect.client import R

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.plugins.commerce.utils import (
    clone_stream,
    display_streams_table,
    export_stream,
    get_destination_account,
    print_errors,
    print_results,
    sync_stream,
)


@group(name='commerce', short_help='Manage commerce definitions.')
def grp_commerce():
    pass  # pragma: no cover


@grp_commerce.group(
    name='stream',
    short_help='Manage commerce streams.',
)
def grp_commerce_streams():
    pass  # pragma: no cover


@grp_commerce_streams.command(
    name='list',
    short_help='List commerce billing and pricing streams.',
)
@click.option(
    '--query',
    '-q',
    'query',
    help='RQL query expression.',
)
@pass_config
def cmd_list_streams(config, query):
    query = query or R()
    display_streams_table(
        config.active.client.ns(
            'billing',
        )
        .streams.filter(
            query,
        )
        .limit(
            console.page_size,
        )
        .select(
            'context',
            'sources',
        ),
        config.active.client.ns(
            'pricing',
        )
        .streams.filter(
            query,
        )
        .limit(
            console.page_size,
        )
        .select(
            'context',
            'sources',
        ),
        config.active.id,
    )


@grp_commerce_streams.command(
    name='export',
    short_help='Export commerce billing or pricing streams.',
)
@click.argument('stream_id', metavar='stream_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--out',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output Excel file name.',
)
@click.option(
    '--output_path',
    '-p',
    'output_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory where to store the export.',
)
@pass_config
def cmd_export_stream(config, stream_id, output_file, output_path):
    export_stream(
        client=config.active.client,
        stream_id=stream_id,
        active_account_id=config.active.id,
        output_file=output_file,
        output_path=output_path,
    )


@grp_commerce_streams.command(
    name='clone',
    short_help='Create a clone of a stream.',
)
@click.argument('source_stream_id', metavar='stream_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--destination_account',
    '-d',
    'destination_account',
    help='Destination account ID',
)
@click.option(
    '--new-stream-name',
    '-n',
    'name',
    help='Cloned stream name',
)
@click.option(
    '--validate',
    '-v',
    is_flag=True,
    help='Executes the validate action after the clone.',
    default=False,
)
@pass_config
def cmd_clone_stream(
    config,
    source_stream_id,
    destination_account,
    name,
    validate,
):
    destination_account_instance = get_destination_account(config, destination_account)

    console.confirm(
        'Are you sure you want to Clone ' f'the stream {source_stream_id} ?',
        abort=True,
    )
    console.echo('')

    stream_id, results = clone_stream(
        origin_account=config.active,
        stream_id=source_stream_id,
        destination_account=destination_account_instance,
        stream_name=name,
        validate=validate,
    )

    console.echo('')

    console.secho(
        f'Stream {source_stream_id} cloned properly to {stream_id}.',
        fg='green',
    )

    console.echo('')

    print_results(results)


@grp_commerce_streams.command(
    name='sync',
    short_help='Synchronize a stream from an excel file.',
)
@click.argument('input_file', metavar='input_file', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_sync_stream(config, input_file):
    stream_id = None
    if '.xlsx' not in input_file:
        stream_id = input_file
        input_file = f'{input_file}/{input_file}.xlsx'
    else:
        stream_id = input_file.split('/')[-1].split('.')[0]
    results, errors = sync_stream(
        account=config.active,
        stream_id=stream_id,
        input_file=input_file,
    )

    console.echo('')

    print_results(results)

    console.echo('')

    print_errors(errors)


def get_group():
    return grp_commerce
