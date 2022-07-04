# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.


import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.core.utils import field_to_check_mark


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
@pass_config
def cmd_list_locales(config, query):
    default_query = config.active.client.ns('localization').locales.all()
    query_locales = default_query.filter(query) if query else default_query

    console.table(
        columns=[
            'ID',
            'Name',
            ('center', 'Autotranslation'),
            ('center', 'Translations'),
        ],
        rows=[
            (
                resource["id"],
                resource["name"],
                field_to_check_mark(resource["auto_translation"], false_value='\u2716'),
                resource["stats"]["translations"] or '-',
            )
            for resource in query_locales
        ],
    )


def get_group():
    return grp_locales
