# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

try:
    import warnings
    from marshmallow.warnings import ChangedInMarshmallow3Warning
    warnings.filterwarnings('ignore', category=ChangedInMarshmallow3Warning)
except ImportError:  # pragma: no cover
    pass

import os

import click

from cnctcli import get_version
from cnctcli.commands.account import grp_account
from cnctcli.commands.product import grp_product
from cnctcli.commands.report import grp_report
from cnctcli.config import pass_config

CCLI_VERSION = get_version()


@click.group()
@click.version_option(version=CCLI_VERSION)
@click.option('-c', '--config-dir',
              default=os.path.join(os.path.expanduser('~'), '.ccli'),
              type=click.Path(file_okay=False),
              help='set the config directory.')
@click.option(
    '-s',
    '--silent',
    is_flag=True,
    help='Prevent the output of informational messages.',
)
@pass_config
def cli(config, config_dir, silent):
    """CloudBlue Connect Command Line Interface"""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config.load(config_dir)
    config.silent = silent


cli.add_command(grp_account)
cli.add_command(grp_product)
cli.add_command(grp_report)


def main():  # pragma: no cover
    print('')
    try:
        cli(prog_name='ccli', standalone_mode=False)  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    except click.ClickException as ce:
        click.echo(
            click.style(str(ce), fg='red')
        )
    except click.exceptions.Abort:
        pass

    print('')


if __name__ == '__main__':
    main()  # pragma: no cover
