import os

from click.testing import CliRunner

from openpyxl import load_workbook

from connect.cli.core.config import Config


def test_not_valid_report_dir(fs, ccli):
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
        ccli,
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
    assert f"The directory `{fs.root_path}/tmp2` is not a reports project root directory." in result.output


def test_no_reports(fs, ccli):
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
        ccli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'list',
            '-d',
            './tests/fixtures/reports/no_reports',
        ],
    )

    assert result.exit_code == 1
    assert 'Invalid `reports.json`: [] is too short' in result.output

    result = runner.invoke(
        ccli,
        [
            'report',
            'info',
            'test',
            '-d',
            './tests/fixtures/reports/no_reports',
        ],
    )

    assert result.exit_code == 1
    assert 'Invalid `reports.json`: [] is too short' in result.output


def test_report_client_exception(fs, ccli):
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
        ccli,
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


def test_report_generic_exception(fs, ccli):
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
        ccli,
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
    assert "Unexpected error while executing the report" in result.output


def test_report_custom_exception(fs, ccli):
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
        ccli,
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


def test_input_parameters(mocker, fs, ccli):
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

    mocker.patch(
        'connect.cli.plugins.report.wizard.dialogus',
        side_effect=[
            {
                'status': 'Active',
            },
            {
                'date': {
                    'from': '2021-01-01',
                    'to': '2021-02-01',
                },
            },
        ],
    )
    result = runner.invoke(
        ccli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/report_with_inputs',
            '-o',
            f'{fs.root_path}/report.xlsx',
        ],
    )

    assert result.exit_code == 0
    assert "100%" in result.output


def test_basic_report(fs, ccli):
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
        ccli,
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


def test_basic_report_2(fs, ccli):

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
        ccli,
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


def test_basic_report_3(fs, ccli):
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
        ccli,
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
    assert 'The report `invalid` does not exist.' in result.output


def test_basic_report_4(fs, ccli):
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
        ccli,
        [
            '-c',
            f'{fs.root_path}/',
            'report',
            'execute',
            'entrypoint',
            '-d',
            './tests/fixtures/reports/basic_report',
            '-o'
            f'{fs.root_path}/report/report',
        ],
    )

    assert result.exit_code == 0
    assert "Processing report test report" in result.output

    wb = load_workbook(f'{fs.root_path}/report/report.xlsx')

    assert wb['Data']['A1'].value == 'Row'
    assert wb['Data']['A2'].value == 1
    assert wb['Data']['A3'].value == 2
    assert wb['Data']['A4'].value is None


def test_basic_report_5(fs, ccli):
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
        ccli,
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

    assert result.exit_code == 1
    assert 'Error: The report `entrypoint_wrong` does not exist.' in result.output
