#  Copyright © 2025 CloudBlue. All rights reserved.

import os
import tempfile

from click.testing import CliRunner


def test_bootstrap_report_command(ccli, mocker, capsys, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_bootstrap = mocker.patch(
            'connect.cli.plugins.project.commands.bootstrap_report_project',
            side_effect=print('project_dir'),
        )
        os.mkdir(f'{tmpdir}/projects')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'report',
                'bootstrap',
                '--output-dir',
                f'{tmpdir}/projects',
            ],
        )
        mocked_bootstrap.assert_called_once_with(f'{tmpdir}/projects', False)
        captured = capsys.readouterr()
        assert 'project_dir' in captured.out
        assert result.exit_code == 0


def test_validate_report_command(ccli, mocker, capsys, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_validate_project = mocker.patch(
            'connect.cli.plugins.project.commands.validate_report_project',
            side_effect=print(
                'Report Project connect/.data/logan has been successfully validated.',
            ),
        )
        os.mkdir(f'{tmpdir}/project')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'report',
                'validate',
                '--project-dir',
                f'{tmpdir}/project',
            ],
        )

        assert result.exit_code == 0
        mocked_validate_project.assert_called_once_with(f'{tmpdir}/project')
        captured = capsys.readouterr()
        assert (
            'Report Project connect/.data/logan has been successfully validated.'
            == captured.out.strip()
        )


def test_add_report_command(ccli, mocker, capsys, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_add_report = mocker.patch(
            'connect.cli.plugins.project.commands.add_report',
            side_effect=print('successfully added'),
        )
        os.mkdir(f'{tmpdir}/project')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'report',
                'add',
                '--project-dir',
                f'{tmpdir}/project',
                '--package-name',
                'reports',
            ],
        )

        assert result.exit_code == 0
        mocked_add_report.assert_called_once_with(f'{tmpdir}/project', 'reports')
        captured = capsys.readouterr()
        assert 'successfully added' == captured.out.strip()


def test_bootstrap_extension_command(ccli, mocker, capsys, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_bootstrap = mocker.patch(
            'connect.cli.plugins.project.commands.bootstrap_extension_project',
            side_effect=print('project_dir'),
        )
        os.mkdir(f'{tmpdir}/projects')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'extension',
                'bootstrap',
                '--output-dir',
                f'{tmpdir}/projects',
                '--save-answers',
                f'{tmpdir}/answers.txt',
            ],
        )

        mocked_bootstrap.assert_called_once()
        captured = capsys.readouterr()
        assert 'project_dir' in captured.out
        assert result.exit_code == 0


def test_bootstrap_extension_command_mutex_options(ccli, mocker, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_bootstrap = mocker.patch(
            'connect.cli.plugins.project.commands.bootstrap_extension_project',
        )
        os.mkdir(f'{tmpdir}/projects')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'extension',
                'bootstrap',
                '--save-answers',
                f'{tmpdir}/answers.txt',
                '--load-answers',
                f'{tmpdir}/sample.txt',
            ],
        )

        mocked_bootstrap.assert_not_called()
        assert result.exit_code != 0
        assert 'Illegal usage' in result.stdout
        assert 'save_answers and load_answers are mutually exclusive' in result.stdout


def test_validate_extension_command(ccli, mocker, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_validate_project = mocker.patch(
            'connect.cli.plugins.project.commands.validate_extension_project',
        )
        os.mkdir(f'{tmpdir}/project')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'extension',
                'validate',
                f'{tmpdir}/project',
            ],
        )
        assert result.exit_code == 0
        mocked_validate_project.assert_called_once()


def test_bump_extension_command(ccli, mocker, capsys, config_mocker):
    with tempfile.TemporaryDirectory() as tmpdir:
        mocked_bump_runner = mocker.patch(
            'connect.cli.plugins.project.commands.bump_runner_extension_project',
            side_effect=print('Runner version has been successfully updated'),
        )
        os.mkdir(f'{tmpdir}/project')
        runner = CliRunner()
        result = runner.invoke(
            ccli,
            [
                'project',
                'extension',
                'bump',
                '--project-dir',
                f'{tmpdir}/project',
            ],
        )

        assert result.exit_code == 0
        mocked_bump_runner.assert_called_once_with(f'{tmpdir}/project')
        captured = capsys.readouterr()
        assert 'Runner version has been successfully updated' == captured.out.strip()


def test_deploy_extension_command(ccli, mocker, config_mocker):
    mocked_deploy_runner = mocker.patch(
        'connect.cli.plugins.project.commands.deploy_extension_project',
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'project',
            'extension',
            'deploy',
            'https://github.com/dummy/repo.git',
        ],
    )

    mocked_deploy_runner.assert_called_once()
    assert result.exit_code == 0
