# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

import click

from connect.client import ConnectClient, RequestLogger
from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.utils import (
    continue_or_quit,
    field_to_check_mark,
    row_format_resource,
    table_formater_resource,
)
from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.shared.utils import wait_for_autotranslation
from connect.cli.plugins.shared.translation_attr_sync import TranslationAttributesSynchronizer
from connect.cli.plugins.translation.constants import TRANSLATION_TABLE_HEADER
from connect.cli.plugins.translation.activate import activate_translation
from connect.cli.plugins.translation.export import dump_translation
from connect.cli.plugins.translation.primarize import primarize_translation
from connect.cli.plugins.translation.translation_sync import TranslationSynchronizer


@group(name='translation', short_help='Manage translations.')
def grp_translation():
    pass  # pragma: no cover


@grp_translation.command(
    name='list',
    short_help='List translations.',
)
@click.option(
    '--query',
    '-q',
    'query',
    help='RQL query expression.',
)
@click.option(
    '--page-size',
    '-p',
    'page_size',
    type=click.IntRange(1),
    help='Number of translations per page.',
    default=25,
)
@click.option(
    '--always-continue',
    '-c',
    'always_continue',
    is_flag=True,
    help='Do not prompt to continue.',
)
@pass_config
def cmd_list_translations(config, query, page_size, always_continue):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )

    default_query = client.ns('localization').translations.all()
    query_translations = default_query.filter(query) if query else default_query

    translation_list = [TRANSLATION_TABLE_HEADER]
    count_of_translations = query_translations.count()

    for paging, resource in enumerate(query_translations, 1):
        owner = field_to_check_mark(acc_id == resource["owner"]["id"])
        primary = field_to_check_mark(resource["primary"])
        row = row_format_resource(
            resource["id"],
            resource["context"]["instance_id"],
            resource["context"]["type"],
            resource["context"]["name"],
            resource["locale"]["name"],
            resource["auto"]["status"],
            resource["status"],
            primary,
            owner,
        )
        translation_list.append(row)
        table_formater_resource(translation_list, count_of_translations, paging, page_size)
        if paging % page_size == 0 and paging != count_of_translations and not always_continue:
            if not continue_or_quit():
                return


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
        config.verbose,
        output_path,
    )
    if not config.silent:
        click.secho(
            f'\nThe translation {translation_id} has been successfully exported to {outfile}.',
            fg='green',
        )


@grp_translation.command(
    name='activate',
    short_help='Active a translation.',
)
@click.argument('translation_id', metavar='TRANSLATION_ID', nargs=1, required=True)
@click.option(
    '--force',
    '-f',
    'force',
    is_flag=True,
    help='Force activate.',
)
@pass_config
def cmd_activate_translation(config, translation_id, force):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
        click.secho(
            'Warning: You are about to activate this translation.\n'
            'Please note that only one translation file may be active for a given locale at a time.\n'
            'Some attributes are not translated and that may cause problems '
            'when using this locale.\n',
            fg='yellow',
        )
    if not force:
        click.confirm(
            f'Are you sure you want to Activate the translation {translation_id} ?',
            abort=True,
        )
        click.echo()
    translation = activate_translation(
        config.active.endpoint,
        config.active.api_key,
        translation_id,
        config.verbose,
    )
    if not config.silent:
        click.secho(
            f'The translation {translation["id"]} on {translation["context"]["name"]} '
            'has been successfully activated.',
            fg='green',
        )


@grp_translation.command(
    name='primarize',
    short_help='Primarize a translation.',
)
@click.argument('translation_id', metavar='TRANSLATION_ID', nargs=1, required=True)
@click.option(
    '--force',
    '-f',
    'force',
    is_flag=True,
    help='Force primarize.',
)
@pass_config
def cmd_primarize_translation(config, translation_id, force):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
        click.secho(
            'Warning: You are about to make this translation primary.\n'
            'This action can\'t be undone.\n'
            'You will loose all of its attributes values, they will be '
            'replaced with the original context attributes values.\n',
            fg='yellow',
        )
        click.secho(
            'Tip: You can clone this translation to keep a copy of the current values.\n',
            fg='blue',
        )
    if not force:
        click.confirm(
            f'Are you sure you want to Primarize the translation {translation_id} ?',
            abort=True,
        )
        click.echo()
    translation = primarize_translation(
        config.active.endpoint,
        config.active.api_key,
        translation_id,
        config.verbose,
    )
    if not config.silent:
        click.secho(
            f'The translation {translation["id"]} on {translation["context"]["name"]} '
            'has been successfully primarize.',
            fg='green',
        )


@grp_translation.command(
    name='sync',
    short_help='Synchronize a translation from an excel file.',
)
@click.argument('input_file', metavar='input_file', nargs=1, required=True)
@click.option(
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.',
)
@pass_config
def cmd_sync_translation(config, input_file, yes):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(f'Current active account: {acc_id} - {acc_name}\n', fg='blue')

    if '.xlsx' not in input_file:
        input_file = f'{input_file}/{input_file}.xlsx'

    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )
    stats = SynchronizerStats()

    translation_sync = TranslationSynchronizer(client, config.silent, acc_id, stats)
    translation_sync.open(input_file)
    translation_id, should_wait_for_autotranslation = translation_sync.sync(yes)
    translation_sync.save(input_file)

    if translation_id:
        if should_wait_for_autotranslation:
            wait_for_autotranslation(client, translation_id, silent=config.silent)
        attributes_sync = TranslationAttributesSynchronizer(client, config.silent, stats)
        attributes_sync.open(input_file, 'Attributes')
        attributes_sync.sync(translation_id)
        attributes_sync.save(input_file)

    if not config.silent:
        stats.print()


def get_group():
    return grp_translation
