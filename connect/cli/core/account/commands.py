# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import click
from click import ClickException
from cmr import render

from connect.cli.core.account.constants import AVAILABLE_ACCOUNTS
from connect.cli.core.account.helpers import (
    activate_account,
    add_account,
    remove_account,
)
from connect.cli.core.config import pass_config
from connect.cli.core.constants import DEFAULT_ENDPOINT


@click.group(name='account', short_help='Manage configured accounts.')
def grp_account():
    pass  # pragma: no cover


@grp_account.command(
    name='add',
    short_help='Add a new account.',
)
@click.argument('api_key', metavar='API_KEY', nargs=1, required=True)  # noqa: E304
@click.option(
    '--endpoint',
    '-e',
    'endpoint',
    default=DEFAULT_ENDPOINT,
    help='API endpoint.',
)
@pass_config
def cmd_add_account(config, api_key, endpoint):
    account_id, name = add_account(config, api_key, endpoint)
    if not config.silent:
        click.secho(f'New account added: {account_id} - {name}', fg='green')


@grp_account.command(
    name='list',
    short_help='List configured accounts.',
)
@pass_config
def cmd_list_account(config):
    if not config.accounts:
        raise ClickException('No account configured.')
    accounts = [AVAILABLE_ACCOUNTS]

    for acc in config.accounts.values():
        active = ' '
        if acc.id == config.active.id:
            active = '\u2713'
        accounts.append(
            f'| {acc.id} | {acc.name} | {active} |\n',
        )

    click.echo(render(''.join(accounts)))


@grp_account.command(
    name='activate',
    short_help='Set the current active account.',
)
@click.argument('id', metavar='ACCOUNT_ID', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_activate_account(config, id):
    acc = activate_account(config, id)
    if not config.silent:
        click.secho(
            f'Current active account is: {acc.id} - {acc.name}',
            fg='green',
        )


@grp_account.command(
    name='remove',
    short_help='Remove a configured account.',
)
@click.argument('id', metavar='ACCOUNT_ID', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_remove_account(config, id):
    acc = remove_account(config, id)
    click.secho(
        f'Account removed: {acc.id} - {acc.name}',
        fg='green',
    )
