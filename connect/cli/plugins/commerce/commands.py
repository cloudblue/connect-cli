# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2023 Ingram Micro. All Rights Reserved.

import click
from connect.client import R

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.plugins.commerce.utils import (
    display_streams_table,
    export_stream,
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


def get_group():
    return grp_commerce
