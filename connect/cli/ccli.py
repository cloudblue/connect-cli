# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import click
import uvloop

from connect.cli.core.base import cli
from connect.cli.core.constants import CAIRO_NOT_FOUND_ERROR
from connect.cli.core.plugins import load_plugins


def main():
    _ignore_openpyxl_warnings()
    uvloop.install()
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


def _ignore_openpyxl_warnings():
    """
    Ignore warning about DataValidation extension not supported. This is shown when a xlsx file
    with unsupported data validation is opened (tipically after saving the file from Excel, which
    uses some custom extension).
    To avoid losing data validation, it should be re-created each time the file is saved by the cli.
    """
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl.worksheet._reader')


if __name__ == '__main__':
    main()  # pragma: no cover
