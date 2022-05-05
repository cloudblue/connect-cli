# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.


import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.utils import (
    continue_or_quit,
    field_to_check_mark,
    row_format_resource,
    table_formater_resource,
)
from connect.cli.plugins.locale.constants import LOCALES_TABLE_HEADER
from connect.client import ConnectClient, RequestLogger


@group(name='locale', short_help='List all locales available.')
def grp_locales():
    pass  # pragma: no cover


@grp_locales.command(
    name='list',
    short_help='List locales.',
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
    help='Number of locales per page.',
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
def cmd_list_locales(config, query, page_size, always_continue):
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

    default_query = client.ns('localization').locales.all()
    query_locales = default_query.filter(query) if query else default_query

    locales_list = [LOCALES_TABLE_HEADER]
    count_of_locales = query_locales.count()

    for paging, resource in enumerate(query_locales, 1):
        auto = field_to_check_mark(resource["auto_translation"], false_value='\u2716')
        translations_count = resource["stats"]["translations"] or '-'
        row = row_format_resource(resource["id"], resource["name"], auto, translations_count)
        locales_list.append(row)
        table_formater_resource(
            locales_list,
            count_of_locales,
            paging,
            page_size,
        )
        if paging % page_size == 0 and paging != count_of_locales and not always_continue:
            if not continue_or_quit():
                return


def get_group():
    return grp_locales
