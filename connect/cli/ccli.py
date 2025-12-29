# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import io
import sys

import click

from connect.cli.core.base import cli
from connect.cli.core.constants import CAIRO_NOT_FOUND_ERROR
from connect.cli.core.plugins import load_plugins


def main():
    _set_stdout_unbuffered()
    _suppress_warnings()
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        pass
    print('')
    try:
        load_plugins(cli)
        cli(prog_name='ccli', standalone_mode=False)
    except OSError as oe:
        if 'no library called "cairo" was found' in str(oe):
            click.secho(CAIRO_NOT_FOUND_ERROR, fg='yellow')
        else:
            click.secho(str(oe), fg='red')
    except click.ClickException as ce:
        click.secho(str(ce), fg='red')
    except click.exceptions.Abort:
        pass
    finally:
        print('')


def _suppress_warnings():
    """
    Suppress all UserWarnings.
    """
    import warnings

    warnings.simplefilter('ignore', category=UserWarning)


def _set_stdout_unbuffered():  # pragma: no cover
    if 'pytest' not in sys.modules:
        sys.stdout = io.TextIOWrapper(open(sys.stdout.fileno(), 'wb', 0), write_through=True)
        sys.stdout.reconfigure(encoding='utf-8')


if __name__ == '__main__':
    main()  # pragma: no cover
