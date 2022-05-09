from click.testing import CliRunner

from openpyxl import load_workbook

from connect.cli.core.config import Config


def test_export(config_mocker, mocker, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.dump_translation',
        side_effect=lambda *args: 'TRN-0000-0000-0000.xlsx',
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'export',
            'TRN-0000-0000-0000',
        ],
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'TRN-0000-0000-0000'
    assert mock.mock_calls[0][1][3] is None
    assert result.exit_code == 0
    assert (
        'The translation TRN-0000-0000-0000 has been successfully '
        'exported to TRN-0000-0000-0000.xlsx.\n' in result.output
    )


def test_export_silent(config_mocker, mocker, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.dump_translation',
        side_effect=lambda *args: 'TRN-0000-0000-0000.xlsx',
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-s',
            'translation',
            'export',
            'TRN-0000-0000-0000',
        ],
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'TRN-0000-0000-0000'
    assert mock.mock_calls[0][1][3] is None
    assert result.exit_code == 0
    assert result.output == ''


def test_list_translations(config_mocker, mocked_responses, mocked_translation_response, ccli):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations',
        headers={
            'Content-Range': 'items 0-0/1',
        },
        json=[mocked_translation_response],
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'list',
        ],
    )
    assert result.exit_code == 0
    assert 'Current active account: VA-000 - Account 0' in result.output
    assert (
        '│TRN-8100-3865-4869│PRD-746-555-769│  product   │translation test product│Spanish│off │active│       │     │' 
        in result.output
    )


def test_activate_translation(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.activate_translation',
        side_effect=lambda *args: mocked_translation_response,
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'activate',
            'TRN-8100-3865-4869',
        ],
        input='y\n',
    )
    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'TRN-8100-3865-4869'
    assert mock.mock_calls[0][1][3] is False
    assert result.exit_code == 0
    assert 'Warning: You are about to activate this translation.' in result.output
    assert (
        'The translation TRN-8100-3865-4869 on translation test '
        'product has been successfully activated.' in result.output
    )


def test_activate_translation_silent(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.activate_translation',
        side_effect=lambda *args: mocked_translation_response,
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-s',
            'translation',
            'activate',
            'TRN-8100-3865-4869',
        ],
        input='y\n',
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'TRN-8100-3865-4869'
    assert mock.mock_calls[0][1][3] is False
    assert result.exit_code == 0
    assert 'Warning: You are about to activate this translation.' not in result.output


def test_abort_activate_translation(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.activate_translation',
        side_effect=lambda *args: mocked_translation_response,
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'activate',
            'TRN-8100-3865-4869',
        ],
        input='n\n',
    )

    mock.assert_not_called()
    assert result.exit_code == 1
    assert 'Aborted!' in result.output


def test_force_activate_translation(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.activate_translation',
        side_effect=lambda *args: mocked_translation_response,
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'activate',
            '-f',
            'TRN-8100-3865-4869',
        ],
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'TRN-8100-3865-4869'
    assert mock.mock_calls[0][1][3] is False
    assert result.exit_code == 0
    assert 'Are you sure you want to Activate the translation TRN-8100-3865-4869 ? [y/N]:' not in result.output
    assert (
        'The translation TRN-8100-3865-4869 on translation test '
        'product has been successfully activated.' in result.output
    )
