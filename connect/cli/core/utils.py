# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.
import os
from collections import OrderedDict
from importlib.metadata import entry_points

from packaging.version import InvalidVersion, Version
import click
import requests

from connect.cli import get_version
from connect.cli.core.constants import PYPI_JSON_API_URL
from connect.cli.core.terminal import console


def _get_correct_sorted_versions(tags):
    versions = []
    for tag in tags:
        try:
            Version(tag)
            versions.append(tag)
        except InvalidVersion:
            continue
    return sorted(versions, key=Version)


def sort_and_filter_tags(tags, desired_major):
    sorted_tags = OrderedDict()
    for tag in _get_correct_sorted_versions(tags.keys()):
        version = Version(tag)
        if str(version.major) != desired_major:
            continue
        sorted_tags[tag] = tags[tag]

    return sorted_tags


def get_last_cli_version():
    try:
        res = requests.get(PYPI_JSON_API_URL)
        if res.status_code == 200:
            data = res.json()
            return data['info']['version']
    except requests.RequestException:
        pass


def check_for_updates(*args):
    current = get_version()
    last_version = get_last_cli_version()
    if last_version and last_version != current:
        console.echo()
        console.secho(
            f'You are running CloudBlue Connect CLI version {current}. '
            f'A newer version is available: {last_version}',
            fg='yellow',
        )
        console.echo()


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


def iter_entry_points(group, name=None):
    group_entrypoints = entry_points().get(group)
    if not group_entrypoints:
        return
    for ep in group_entrypoints:
        if name:
            if ep.name == name:
                yield ep
        else:
            yield ep
