#  Copyright © 2021 CloudBlue. All rights reserved.

from click.testing import CliRunner

import os


def test_bootstrap_report_command(fs, ccli, mocker, capsys):
    mocked_bootstrap = mocker.patch(
        'connect.cli.plugins.project.commands.bootstrap_report_project',
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
            '--output-dir',
            f'{fs.root_path}/projects',
        ],
    )

    mocked_bootstrap.assert_called_once_with(f'{fs.root_path}/projects')
    captured = capsys.readouterr()
    assert 'project_dir' in captured.out
    assert result.exit_code == 0


def test_validate_report_command(fs, ccli, mocker, capsys):
    mocked_validate_project = mocker.patch(
        'connect.cli.plugins.project.commands.validate_report_project',
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
    assert 'Report Project connect/.data/logan has been successfully validated.' == captured.out.strip()


def test_add_report_command(fs, ccli, mocker, capsys):
    mocked_add_report = mocker.patch(
        'connect.cli.plugins.project.commands.add_report',
        side_effect=print('successfully added'),
    )
    os.mkdir(f'{fs.root_path}/project')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'report',
            'add',
            '--project-dir',
            f'{fs.root_path}/project',
            '--package-name',
            'reports',
        ],
    )

    assert result.exit_code == 0
    mocked_add_report.assert_called_once_with(f'{fs.root_path}/project', 'reports')
    captured = capsys.readouterr()
    assert 'successfully added' == captured.out.strip()


def test_bootstrap_extension_command(fs, ccli, mocker, capsys):
    mocked_bootstrap = mocker.patch(
        'connect.cli.plugins.project.commands.bootstrap_extension_project',
        side_effect=print('project_dir'),
    )
    os.mkdir(f'{fs.root_path}/projects')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'extension',
            'bootstrap',
            '--output-dir',
            f'{fs.root_path}/projects',
        ],
    )

    mocked_bootstrap.assert_called_once()
    captured = capsys.readouterr()
    assert 'project_dir' in captured.out
    assert result.exit_code == 0


def test_validate_extension_command(fs, ccli, mocker, capsys):
    mocked_validate_project = mocker.patch(
        'connect.cli.plugins.project.commands.validate_extension_project',
        side_effect=print('Extension Project connect/.data/logan has been successfully validated.'),
    )
    os.mkdir(f'{fs.root_path}/project')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'extension',
            'validate',
            '--project-dir',
            f'{fs.root_path}/project',
        ],
    )

    assert result.exit_code == 0
    mocked_validate_project.assert_called_once_with(f'{fs.root_path}/project')
    captured = capsys.readouterr()
    assert 'Extension Project connect/.data/logan has been successfully validated.' == captured.out.strip()


def test_bump_extension_command(fs, ccli, mocker, capsys):
    mocked_bump_runner = mocker.patch(
        'connect.cli.plugins.project.commands.bump_runner_extension_project',
        side_effect=print('Runner version has been successfully updated'),
    )
    os.mkdir(f'{fs.root_path}/project')
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'extension',
            'bump',
            '--project-dir',
            f'{fs.root_path}/project',
        ],
    )

    assert result.exit_code == 0
    mocked_bump_runner.assert_called_once_with(f'{fs.root_path}/project')
    captured = capsys.readouterr()
    assert 'Runner version has been successfully updated' == captured.out.strip()
