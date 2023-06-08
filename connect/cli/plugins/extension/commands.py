# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2023 Ingram Micro. All Rights Reserved.

import click

from connect.cli.core import group
from connect.cli.core.config import pass_config


@group(name='extension', short_help='Manage extension deployment.')
def grp_extension():
    pass  # pragma: no cover


@grp_extension.command(
    name='install',
    short_help='Install extension.',
)
@click.option(
    '--repo',
    '-r',
    'repo',
    help='Repository URL.',
)
@pass_config
def cmd_install_extension(config, repo):
    account_id = config.active.id
    client = config.active.client


@grp_extension.command(
    name='update',
    short_help='Update extension.',
)
@click.option(
    '--repo',
    '-r',
    'repo',
    help='Repository URL.',
)
@pass_config
def cmd_update_extension(config, repo):
    pass


def get_group():
    return grp_extension
