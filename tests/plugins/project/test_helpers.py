#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import json

import pytest

from click import ClickException

from cookiecutter.config import DEFAULT_CONFIG
from cookiecutter.exceptions import OutputDirExistsException

from connect.cli.plugins.project.helpers import (
    bootstrap_project,
    list_projects,
)


def test_bootstrap_project(fs, mocker, capsys):
    mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        return_value='project_dir',
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    data_dir = f'{fs.root_path}/projects'
    os.mkdir(data_dir)
    bootstrap_project(data_dir)

    captured = capsys.readouterr()
    assert 'project_dir' in captured.out


def test_bootstrap_direxists_error(fs, mocker):
    mocked_cookiecutter = mocker.patch(
        'connect.cli.plugins.project.helpers.cookiecutter',
        side_effect=OutputDirExistsException('dir "project_dir" exists'),
    )
    cookie_dir = f'{fs.root_path}/.cookiecutters'
    os.mkdir(cookie_dir)
    DEFAULT_CONFIG['cookiecutters_dir'] = cookie_dir

    data_dir = f'{fs.root_path}/projects'
    os.mkdir(data_dir)

    with pytest.raises(ClickException):
        bootstrap_project(data_dir)
    assert mocked_cookiecutter.call_count == 1


def test_list_projects_empty_dir(fs, mocker, capsys):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=[],
    )
    list_projects(fs.root_path)

    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    captured = capsys.readouterr()
    assert 'No projects found!' in captured.out


def test_list_projects_wrong_json(fs, mocker):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=['project1/reports.json'],
    )
    mocker.patch(
        'connect.cli.plugins.project.helpers.open',
        return_value='super-duper content',
    )
    mocked_load = mocker.patch(
        'connect.cli.plugins.project.helpers.json.load',
        side_effect=json.JSONDecodeError(msg='error', doc='error', pos=1),
    )
    with pytest.raises(ClickException):
        list_projects(fs.root_path)
    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    mocked_load.assert_called_once_with('super-duper content')


def test_list_projects(fs, mocker, mocked_reports, capsys):
    mocked_glob = mocker.patch(
        'connect.cli.plugins.project.helpers.glob.glob',
        return_value=['project1/reports.json'],
    )
    project_one = mocked_reports
    mocker.patch(
        'connect.cli.plugins.project.helpers.open',
    )
    mocker.patch(
        'connect.cli.plugins.project.helpers.json.load',
        return_value=project_one,
    )
    list_projects(fs.root_path)

    mocked_glob.assert_called_once_with(f'{fs.root_path}/**/reports.json')
    captured = capsys.readouterr()
    assert 'Connect Reports' in captured.out
