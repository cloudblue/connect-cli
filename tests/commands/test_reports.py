from click.testing import CliRunner

from cnctcli.ccli import cli
from openpyxl import load_workbook

from cnctcli.config import Config

from unittest.mock import patch

import os


def test_not_valid_report_dir(fs):
    config = Config()
    config._config_path = '/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    os.mkdir('/tmp2')
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'report',
            'list',
            '-d',
            '/tmp2',
        ],
    )

    assert result.exit_code == 1
    assert "The directory /tmp2 is not a report project root directory." in result.output


def test_no_reports(fs):
    fs.add_real_file('./tests/fixtures/reports/no_reports/reports.json')
    fs.add_real_file('./tests/fixtures/reports/no_reports/README.md')
    config = Config()
    config._config_path = '/config.json'
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
    fs.add_real_file('./tests/fixtures/reports/connect_exception/reports.json')
    fs.add_real_file('./tests/fixtures/reports/connect_exception/README.md')
    fs.add_real_file('./tests/fixtures/reports/connect_exception/entrypoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/connect_exception/entrypoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/connect_exception/entrypoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/connect_exception/entrypoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
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
    fs.add_real_file('./tests/fixtures/reports/generic_exception/reports.json')
    fs.add_real_file('./tests/fixtures/reports/generic_exception/README.md')
    fs.add_real_file('./tests/fixtures/reports/generic_exception/entry_point/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/generic_exception/entry_point/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/generic_exception/entry_point/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/generic_exception/entry_point/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
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
    fs.add_real_file('./tests/fixtures/reports/custom_exception/reports.json')
    fs.add_real_file('./tests/fixtures/reports/custom_exception/README.md')
    fs.add_real_file('./tests/fixtures/reports/custom_exception/entry__point/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/custom_exception/entry__point/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/custom_exception/entry__point/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/custom_exception/entry__point/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
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
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/reports.json')
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/README.md')
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/executor/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/executor/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/executor/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/report_with_inputs/executor/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
                '/',
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
    fs.add_real_file('./tests/fixtures/reports/basic_report/reports.json')
    fs.add_real_file('./tests/fixtures/reports/basic_report/README.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
            'report',
            'list',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert "Connect Reports Fixture version 1.0.0" in result.output


def test_basic_report_2(fs):
    fs.add_real_file('./tests/fixtures/reports/basic_report/reports.json')
    fs.add_real_file('./tests/fixtures/reports/basic_report/README.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
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
    fs.add_real_file('./tests/fixtures/reports/basic_report/reports.json')
    fs.add_real_file('./tests/fixtures/reports/basic_report/README.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
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
    fs.add_real_file('./tests/fixtures/reports/basic_report/reports.json')
    fs.add_real_file('./tests/fixtures/reports/basic_report/README.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://localhost/public/v1',
    )
    config.activate('VA-000')
    config.store()
    runner = CliRunner()
    os.mkdir('/report')
    result = runner.invoke(
        cli,
        [
            '-c',
            '/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/basic_report',
            '-o'
            '/report/report.xlsx'
        ],
    )

    assert result.exit_code == 0
    assert "Processing report test report" in result.output

    wb = load_workbook('/report/report.xlsx')

    assert wb['Data']['A1'].value == 'Row'
    assert wb['Data']['A2'].value == 1
    assert wb['Data']['A3'].value == 2
    assert wb['Data']['A4'].value is None


def test_basic_report_5(fs):
    fs.add_real_file('./tests/fixtures/reports/basic_report/reports.json')
    fs.add_real_file('./tests/fixtures/reports/basic_report/README.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/__init__.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/entrypoint.py')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/Readme.md')
    fs.add_real_file('./tests/fixtures/reports/basic_report/endpoint/template.xlsx')

    config = Config()
    config._config_path = '/config.json'
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
            '/',
            'report',
            'info',
            'entrypoint_wrong',
            '-d',
            './tests/fixtures/reports/basic_report',
        ],
    )

    assert result.exit_code == 0
    assert "No report with id entrypoint_wrong" in result.output