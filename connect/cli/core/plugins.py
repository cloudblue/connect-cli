# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.
import click

from connect.cli.core.utils import iter_entry_points


def load_plugins(cli):
    @click.group(name='plugin', short_help='Third party plugins.')
    def grp_plugins():
        pass  # pragma: no cover

    has_3rd_party_plugins = False

    for entrypoint in iter_entry_points('connect.cli.plugins'):
        if entrypoint.value.startswith('connect.cli.plugins.'):
            command_fn = entrypoint.load()
            cli.add_command(command_fn())
        else:
            has_3rd_party_plugins = True
            command_fn = entrypoint.load()
            grp_plugins.add_command(command_fn())

    if has_3rd_party_plugins:
        cli.add_command(grp_plugins)
