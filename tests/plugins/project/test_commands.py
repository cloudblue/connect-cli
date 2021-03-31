#  Copyright © 2021 CloudBlue. All rights reserved.

from click.testing import CliRunner

import os


def test_bootstrap_command(fs, ccli, mocker, capsys):
    mocked_bootstrap = mocker.patch(
        'connect.cli.plugins.project.commands.bootstrap_project',
        side_effect=print('project_dir'),
    )
    os.mkdir(f'{fs.root_path}/projects')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'report',
            'bootstrap',
            '--data-dir',
            f'{fs.root_path}/projects',
        ],
    )

    mocked_bootstrap.assert_called_once_with(f'{fs.root_path}/projects')
    captured = capsys.readouterr()
    assert 'project_dir' in captured.out
    assert result.exit_code == 0


def test_list_project_command(fs, ccli, mocker, capsys):
    mocked_list_project = mocker.patch(
        'connect.cli.plugins.project.commands.list_projects',
        side_effect=print('project_1'),
    )
    os.mkdir(f'{fs.root_path}/projects')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'report',
            'list',
            '--data-dir',
            f'{fs.root_path}/projects',
        ],
    )

    assert result.exit_code == 0
    mocked_list_project.assert_called_once_with(f'{fs.root_path}/projects')
    captured = capsys.readouterr()
    assert 'project_1' in captured.out


def test_validate_command(fs, ccli, mocker, capsys):
    mocked_validate_project = mocker.patch(
        'connect.cli.plugins.project.commands.validate_project',
        side_effect=print('Report Project connect/.data/logan has been successfully validated.'),
    )
    os.mkdir(f'{fs.root_path}/project')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'report',
            'validate',
            '--project-dir',
            f'{fs.root_path}/project',
        ],
    )

    assert result.exit_code == 0
    mocked_validate_project.assert_called_once_with(f'{fs.root_path}/project')
    captured = capsys.readouterr()
    assert 'Report Project connect/.data/logan has been successfully validated.' in captured.out
