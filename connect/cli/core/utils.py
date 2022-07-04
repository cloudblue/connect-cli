# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.
import os

import click
import requests

from connect.cli import get_version
from connect.cli.core.constants import PYPI_JSON_API_URL
from connect.cli.core.terminal import console


def check_for_updates(*args):
    try:
        res = requests.get(PYPI_JSON_API_URL)
        if res.status_code == 200:
            data = res.json()
            version = data['info']['version']
            current = get_version()
            if version != current:
                console.echo()
                console.secho(
                    f'You are running CloudBlue Connect CLI version {current}. '
                    f'A newer version is available: {version}.',
                    fg='yellow',
                )
                console.echo()
    except requests.RequestException:
        pass


def validate_output_options(output_path, output_file, default_dir_name, default_file_name=None):
    """
    Common validation for commands using output path and file options.
    """
    if not default_file_name:
        default_file_name = default_dir_name

    output_path = output_path or os.getcwd()
    if not os.path.exists(output_path):
        raise click.ClickException("Output Path does not exist")

    output_path = os.path.join(output_path, default_dir_name)
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    elif not os.path.isdir(output_path):  # pragma: no branch
        raise click.ClickException(
            f"Exists a file with name '{os.path.basename(output_path)}' but a directory is "
            "expected, please rename it",
        )

    output_file = os.path.join(output_path, output_file or f'{default_file_name}.xlsx')

    return output_file


def field_to_check_mark(predicate, false_value=''):
    """Change the value of a field to a check mark base on a predicate.

        :param predicate: bool value / expression.
        :param false_value: customizable value if predicate evaluates to false.
        """
    return (
        '\u2713' if predicate else false_value
    )


def row_format_resource(*fields):
    """Transform a variable number of fields to a `table-row` format.
        ```
            >>> row_format_resource(a,b,c,d)
            '| a | b | c | d |'
        ```
        :param fields: fields to be converted to row.
        """
    return ('| {} ' * len(fields)).format(*fields) + '|\n'  # noqa: P103
