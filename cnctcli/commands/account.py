# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click

from cnctcli.actions.accounts import (
    activate_account,
    add_account,
    remove_account,
)
from cnctcli.config import pass_config
from cnctcli.constants import DEFAULT_ENDPOINT


@click.group(name='account', short_help='account configuration')
def grp_account():
    pass  # pragma: no cover


@grp_account.command(
    name='add',
    short_help='add a new account',
)
@click.argument('api_key', metavar='API_KEY', nargs=1, required=True)  # noqa: E304
@click.option(
    '--endpoint',
    '-e',
    'endpoint',
    default=DEFAULT_ENDPOINT,
    help='API endpoint.'
)
@pass_config
def cmd_add_account(config, api_key, endpoint):
    account_id, name = add_account(config, api_key, endpoint)
    if not config.silent:
        click.echo(
            click.style(f'New account added: {account_id} - {name}', fg='green')
        )


@grp_account.command(
    name='list',
    short_help='list configured accounts',
)
@pass_config
def cmd_list_account(config):
    for acc in config.accounts.values():
        if acc.id == config.active.id:
            click.echo(
                click.style(
                    f'{acc.id} - {acc.name} (active)',
                    fg='blue',
                ),
            )
        else:
            click.echo(f'{acc.id} - {acc.name}')


@grp_account.command(
    name='activate',
    short_help='set active account',
)
@click.argument('id', metavar='ACCOUNT_ID', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_activate_account(config, id):
    acc = activate_account(config, id)
    if not config.silent:
        click.echo(
            click.style(
                f'Current active account is: {acc.id} - {acc.name}',
                fg='green',
            ),
        )


@grp_account.command(
    name='remove',
    short_help='remove an account',
)
@click.argument('id', metavar='ACCOUNT_ID', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_remove_account(config, id):
    acc = remove_account(config, id)
    click.echo(
        click.style(
            f'Account removed: {acc.id} - {acc.name}',
            fg='green',
        ),
    )
