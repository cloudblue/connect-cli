# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import json
import subprocess

import click


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
        out = subprocess.check_output(['pip', 'list', '-o', '--format', 'json'])
        data = json.loads(out)
        me = next(filter(lambda p: p['name'] == 'connect-cli', data))
        click.secho(
            f'\nYou are running CloudBlue Connect CLI version {me["version"]}. '
            f'A newer version is available: {me["latest_version"]}.\n',
            fg='yellow',
        )
    except (subprocess.CalledProcessError, StopIteration):
        pass
