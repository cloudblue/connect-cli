# -*- coding: utf-8 -*-

# This file is part of the CloudBlue Connect connect-cli.
# Copyright (c) 2019-2025 CloudBlue. All Rights Reserved.
import click

from connect.cli.core.utils import iter_entry_points


# The built-in command groups by entry point: their command name and the short help that
# `ccli --help` shows. Knowing them up front, ccli imports a group only when it runs: some
# pull in heavy libraries, such as WeasyPrint for the PDF reports.
# tests/core/test_plugins.py checks this table against the groups themselves.
BUILTIN_GROUPS = {
    'commerce': ('commerce', 'Manage commerce definitions.'),
    'customer': ('customer', 'Export/synchronize customers.'),
    'locales': ('locale', 'List all locales available.'),
    'play': ('play', 'Play connect scripts.'),
    'product': ('product', 'Manage product definitions.'),
    'project': ('project', 'Manage project definitions.'),
    'report': ('report', 'Reports execution and development.'),
    'translation': ('translation', 'Manage translations.'),
}


def load_plugins(cli):
    @click.group(name='plugin', short_help='Third party plugins.')
    def grp_plugins():
        pass  # pragma: no cover

    has_3rd_party_plugins = False

    for entrypoint in iter_entry_points('connect.cli.plugins'):
        if (
            entrypoint.value.startswith('connect.cli.plugins.')
            and entrypoint.name in BUILTIN_GROUPS
        ):
            cli.add_lazy_command(*BUILTIN_GROUPS[entrypoint.name], entrypoint)
        elif entrypoint.value.startswith('connect.cli.plugins.'):
            command_fn = entrypoint.load()
            cli.add_command(command_fn())
        else:
            has_3rd_party_plugins = True
            command_fn = entrypoint.load()
            grp_plugins.add_command(command_fn())

    if has_3rd_party_plugins:
        cli.add_command(grp_plugins)
