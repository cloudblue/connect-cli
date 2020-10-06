# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

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
