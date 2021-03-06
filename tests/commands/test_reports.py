from click.testing import CliRunner

from cnctcli.ccli import cli
from openpyxl import load_workbook

from cnctcli.config import Config

from unittest.mock import patch

import os


def test_not_valid_report_dir(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    os.mkdir(f'{fs.root_path}/tmp2')
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'list',
            '-d',
            f'{fs.root_path}/tmp2',
        ],
    )

    assert result.exit_code == 1
    assert f"The directory {fs.root_path}/tmp2 is not a report project root directory." in result.output


def test_no_reports(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'list',
            '-d',
            './tests/fixtures/reports/no_reports',
        ],
    )

    assert result.exit_code == 0
    assert "No reports found in" in result.output

    result = runner.invoke(
        cli,
        [
            'report',
            'info',
            'test',
            '-d',
            './tests/fixtures/reports/no_reports',
        ],
    )

    assert result.exit_code == 0
    assert "No reports found in" in result.output


def test_report_client_exception(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/connect_exception',
        ],
    )

    assert result.exit_code == 1
    assert "Error returned by Connect when executing the report" in result.output


def test_report_generic_exception(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/generic_exception',
        ],
    )

    assert result.exit_code == 1
    assert "Unknown error while executing the report" in result.output


def test_report_custom_exception(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/custom_exception',
        ],
    )

    assert result.exit_code == 1
    assert "Custom error" in result.output


def test_input_parameters(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()

    with patch(
        'cnctcli.actions.reports.dialogus',
        side_effect=[
            {
                'status': 'Active'
            },
            {
                'date': {
                    'from': '2021-01-01',
                    'to': '2021-02-01',
                },
            },
        ]
    ):
        result = runner.invoke(
            cli,
            [
                '-c',
                f'{fs.root_path}/',
                'report',
                'execute',
                'entrypoint',
                '-d',
                './tests/fixtures/reports/report_with_inputs',
            ],
        )

        assert result.exit_code == 0
        assert "100%" in result.output


def test_basic_report(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'list',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert "Connect Reports Fixture version 1.0.0" in result.output


def test_basic_report_2(fs):

    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'info',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert result.exit_code == 0
    assert "Basic report info" in result.output


def test_basic_report_3(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'invalid',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert result.exit_code == 1
    assert "No report with id invalid has been found." in result.output


def test_basic_report_4(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    os.mkdir(f'{fs.root_path}/report')
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/basic_report',
            '-o'
            f'{fs.root_path}/report/report.xlsx'
        ],
    )

    assert result.exit_code == 0
    assert "Processing report test report" in result.output

    wb = load_workbook(f'{fs.root_path}/report/report.xlsx')

    assert wb['Data']['A1'].value == 'Row'
    assert wb['Data']['A2'].value == 1
    assert wb['Data']['A3'].value == 2
    assert wb['Data']['A4'].value is None


def test_basic_report_5(fs):
    config = Config()
    config._config_path = f'{fs.root_path}/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'info',
            'entrypoint_wrong',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert result.exit_code == 0
    assert "No report with id entrypoint_wrong" in result.output