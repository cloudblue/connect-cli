# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.plugins.translation.export import dump_translation


@group(name='translation', short_help='Manage translations.')
def grp_translation():
    pass  # pragma: no cover


@grp_translation.command(
    name='export',
    short_help='Export a translation and its attributes to an excel file.',
)
@click.argument('translation_id', metavar='translation_id', nargs=1, required=True)
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
def cmd_export_translation(config, translation_id, output_file, output_path):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    outfile = dump_translation(
        config.active.endpoint,
        config.active.api_key,
        translation_id,
        output_file,
        config.silent,
        config.verbose,
        output_path,
    )
    if not config.silent:
        click.secho(
            f'\nThe translation {translation_id} has been successfully exported to {outfile}.',
            fg='green',
        )


def get_group():
    return grp_translation
