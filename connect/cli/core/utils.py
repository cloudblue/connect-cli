# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import click
import requests

from connect.cli import get_version
from connect.cli.core.constants import PYPI_JSON_API_URL


def continue_or_quit():
    while True:
        click.echo('')
        click.echo("Press 'c' to continue or 'q' to quit ", nl=False)
        c = click.getchar()
        click.echo()
        if c == 'c':
            return True
        if c == 'q':
            return False


def check_for_updates(*args):
    try:
        res = requests.get(PYPI_JSON_API_URL)
        if res.status_code == 200:
            data = res.json()
            version = data['info']['version']
            current = get_version()
            if version != current:
                click.secho(
                    f'\nYou are running CloudBlue Connect CLI version {current}. '
                    f'A newer version is available: {version}.\n',
                    fg='yellow',
                )
    except requests.RequestException:
        pass
