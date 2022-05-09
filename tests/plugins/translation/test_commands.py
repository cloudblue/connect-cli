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
    print(result.output)
    assert result.exit_code == 0
    assert 'Current active account: VA-000 - Account 0' in result.output
    assert (
        '│TRN-8100-3865-4869│PRD-746-555-769│  product   │translation test product│Spanish│off │active│       │     │'
        in result.output
    )
