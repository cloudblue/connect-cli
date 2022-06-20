import json

import pytest
from click import ClickException

from connect.cli.core.config import Config
from connect.cli.plugins.report.helpers import (
    execute_report,
    list_reports,
    load_repo,
    show_report_info,
)
from connect.cli.plugins.report.utils import Progress
from connect.client import ConnectClient
from connect.reports.datamodels import RendererDefinition, ReportDefinition


def test_load_repo_ok():
    repo = load_repo('./tests/fixtures/reports/basic_report')
    assert repo is not None


def test_load_repo_no_descriptor():
    with pytest.raises(ClickException) as cv:
        load_repo('/tmp')

    assert str(cv.value) == 'The directory `/tmp` is not a reports project root directory.'


def test_load_repo_descriptor_unparseable(mocker):
    mocker.patch(
        'connect.cli.plugins.report.helpers.json.load',
        side_effect=json.JSONDecodeError('test', 'json_doc', 1),
    )
    with pytest.raises(ClickException) as cv:
        load_repo('./tests/fixtures/reports/basic_report')

    assert str(cv.value) == 'The reports project descriptor `reports.json` is not a valid json file.'


def test_load_repo_descriptor_invalid_json(mocker):
    mocker.patch(
        'connect.cli.plugins.report.helpers.validate_with_schema',
        return_value='these are errors',
    )
    with pytest.raises(ClickException) as cv:
        load_repo('./tests/fixtures/reports/basic_report')

    assert str(cv.value) == 'Invalid `reports.json`: these are errors'


def test_load_repo_invalid_repo(mocker):
    mocker.patch(
        'connect.cli.plugins.report.helpers.validate',
        return_value=['these are errors'],
    )
    with pytest.raises(ClickException) as cv:
        load_repo('./tests/fixtures/reports/basic_report')

    assert str(cv.value) == 'Invalid `reports.json`: these are errors'


def test_list_reports(capsys):
    list_reports('./tests/fixtures/reports/basic_report')
    captured = capsys.readouterr()
    assert '│ entrypoint │ test report │' in captured.out


def test_show_report_info(mocker):
    mocked_table = mocker.patch(
        'connect.cli.plugins.report.helpers.console.table',
    )

    show_report_info('./tests/fixtures/reports/report_v2', 'test_v2')

    assert mocked_table.mock_calls[0].kwargs['rows'] == [
        ('xlsx', 'Export data in Microsoft Excel 2020 format.', ''),
        ('json', 'Export data as JSON', ''),
        ('pdf-portrait', 'Export data as PDF', '✓'),
    ]


@pytest.mark.parametrize(
    ('account_id', 'audience', 'expected_error'),
    (
        ('VA-000', 'provider', 'This report is not expected to be executed on vendor accounts'),
        ('PA-000', 'vendor', 'This report is not expected to be executed on provider accounts'),

    ),
)
def test_execute_report_invalid_account(mocker, account_id, audience, expected_error):
    config = Config()
    config.add_account(
        account_id,
        'Account 1',
        'ApiKey XXXX:YYYY',
    )
    config.activate(account_id)

    mocker.patch('connect.cli.plugins.report.helpers.load_repo')

    mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_by_id',
        return_value=mocker.MagicMock(audience=[audience]),
    )

    with pytest.raises(ClickException) as cv:
        execute_report(config, 'root_dir', 'local_id', 'out_file', 'out_format')

    assert str(cv.value) == expected_error


def test_execute_report_invalid_renderer(mocker):
    config = Config()
    config.add_account(
        'VA-000-001',
        'Account 1',
        'ApiKey XXXX:YYYY',
    )
    config.activate('VA-000-001')

    mocker.patch('connect.cli.plugins.report.helpers.load_repo')

    mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_by_id',
        return_value=mocker.MagicMock(
            renderers=[
                RendererDefinition('path', 'pdf', 'pdf', 'test'),
            ],
            audience=['vendor'],
        ),
    )

    with pytest.raises(ClickException) as cv:
        execute_report(config, 'root_dir', 'local_id', 'out_file', 'out_format')

    assert str(cv.value) == 'The format out_format is not available for report local_id'


def test_execute_report_v1(mocker):
    report_data = [('a', 'b', 'c')]
    param_inputs = {'param_id': 'param_value'}
    mocked_input = mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_inputs',
        return_value=param_inputs,
    )
    renderer_mock = mocker.MagicMock()
    renderer_mock.render.return_value = 'outfile.ext'
    mocker.patch(
        'connect.cli.plugins.report.helpers.get_renderer',
        return_value=renderer_mock,
    )
    ep_mock = mocker.MagicMock()
    mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_entrypoint',
        return_value=ep_mock,
    )
    ep_mock.return_value = report_data
    config = Config()
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
    )
    config.activate('VA-000')

    execute_report(
        config, './tests/fixtures/reports/basic_report',
        'entrypoint', 'out_file', None,
    )

    assert mocked_input.mock_calls[0].args[0] == config
    assert isinstance(mocked_input.mock_calls[0].args[1], ConnectClient)
    assert isinstance(mocked_input.mock_calls[0].args[2], ReportDefinition)

    assert renderer_mock.render.mock_calls[0].args[0] == report_data
    assert renderer_mock.render.mock_calls[0].args[1] == 'out_file'
    assert isinstance(ep_mock.mock_calls[0].args[0], ConnectClient)
    assert ep_mock.mock_calls[0].args[1] == param_inputs
    assert isinstance(ep_mock.mock_calls[0].args[2], Progress)


def test_execute_report_v2(mocker):
    report_data = [('a', 'b', 'c')]
    param_inputs = {'param_id': 'param_value'}
    mocked_input = mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_inputs',
        return_value=param_inputs,
    )
    ex_ctx_callback = mocker.MagicMock()
    renderer_mock = mocker.MagicMock()
    renderer_mock.type = 'pdf'
    renderer_mock.render.return_value = 'outfile.pdf'
    renderer_mock.set_extra_context = ex_ctx_callback
    mocker.patch(
        'connect.cli.plugins.report.helpers.get_renderer',
        return_value=renderer_mock,
    )
    ep_mock = mocker.MagicMock()
    mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_entrypoint',
        return_value=ep_mock,
    )
    ep_mock.return_value = report_data
    config = Config()
    config.add_account(
        'PA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
    )
    config.activate('PA-000')

    execute_report(
        config, './tests/fixtures/reports/report_v2',
        'test_v2', 'out_file', None,
    )

    assert mocked_input.mock_calls[0].args[0] == config
    assert isinstance(mocked_input.mock_calls[0].args[1], ConnectClient)
    assert isinstance(mocked_input.mock_calls[0].args[2], ReportDefinition)

    assert renderer_mock.render.mock_calls[0].args[0] == report_data
    assert renderer_mock.render.mock_calls[0].args[1] == 'out_file'
    assert isinstance(ep_mock.mock_calls[0].args[0], ConnectClient)
    assert ep_mock.mock_calls[0].args[1] == param_inputs
    assert isinstance(ep_mock.mock_calls[0].args[2], Progress)
    assert ep_mock.mock_calls[0].args[3] == 'pdf'
    assert ep_mock.mock_calls[0].args[4] == ex_ctx_callback


def test_execute_report_fail(mocker):
    mocker.patch('connect.cli.plugins.report.helpers.get_report_inputs')
    mocker.patch('connect.cli.plugins.report.helpers.get_renderer')
    ep_mock = mocker.MagicMock()
    mocker.patch(
        'connect.cli.plugins.report.helpers.get_report_entrypoint',
        return_value=ep_mock,
    )
    ep_mock.side_effect = Exception('this is an error')
    mocked_handle_exc = mocker.patch('connect.cli.plugins.report.helpers.handle_report_exception')
    config = Config()
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
    )
    config.activate('VA-000')

    execute_report(
        config, './tests/fixtures/reports/basic_report',
        'entrypoint', 'out_file', None,
    )

    mocked_handle_exc.assert_called_once()
