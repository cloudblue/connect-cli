from click.testing import CliRunner


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
    assert mock.mock_calls[0][1][1] == 'TRN-0000-0000-0000'
    assert mock.mock_calls[0][1][2] is None
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
    assert mock.mock_calls[0][1][1] == 'TRN-0000-0000-0000'
    assert mock.mock_calls[0][1][2] is None
    assert result.exit_code == 0
    assert result.output == ''


def test_list_translations(
    config_mocker,
    console_80_columns,
    mocked_responses,
    mocked_translation_response,
    ccli,
):
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
        '│ TRN-8… │ PRD-7… │ produ… │ trans… │ Spanish │ off  │ active │        │       │'
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
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

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
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

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
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

    assert result.exit_code == 0
    assert (
        'Are you sure you want to Activate the translation TRN-8100-3865-4869 ? [y/N]:'
        not in result.output
    )
    assert (
        'The translation TRN-8100-3865-4869 on translation test '
        'product has been successfully activated.' in result.output
    )


def test_primarize_translation_command(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.primarize_translation',
        side_effect=lambda *args: mocked_translation_response,
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'primarize',
            'TRN-8100-3865-4869',
        ],
        input='y\n',
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

    assert result.exit_code == 0
    assert 'Warning: You are about to make this translation primary.' in result.output
    assert (
        'The translation TRN-8100-3865-4869 on translation test '
        'product has been successfully primarize.' in result.output
    )


def test_primarize_translation_silent(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.primarize_translation',
        side_effect=lambda *args: mocked_translation_response,
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-s',
            'translation',
            'primarize',
            'TRN-8100-3865-4869',
        ],
        input='y\n',
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

    assert result.exit_code == 0
    assert 'Warning: You are about to make this translation primary.' not in result.output


def test_abort_primarize_translation(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.primarize_translation',
        side_effect=lambda *args: mocked_translation_response,
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'primarize',
            'TRN-8100-3865-4869',
        ],
        input='n\n',
    )

    mock.assert_not_called()
    assert result.exit_code == 1
    assert 'Aborted!' in result.output


def test_force_primarize_translation(config_mocker, mocker, mocked_translation_response, ccli):
    mock = mocker.patch(
        'connect.cli.plugins.translation.commands.primarize_translation',
        side_effect=lambda *args: mocked_translation_response,
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'translation',
            'primarize',
            '-f',
            'TRN-8100-3865-4869',
        ],
    )

    mock.assert_called_once()
    assert mock.mock_calls[0][1][1] == 'TRN-8100-3865-4869'

    assert result.exit_code == 0
    assert (
        'Are you sure you want to Primarize the translation TRN-8100-3865-4869 ?'
        not in result.output
    )
    assert (
        'The translation TRN-8100-3865-4869 on translation test '
        'product has been successfully primarize.' in result.output
    )


def test_sync_command_ok(config_mocker, fs, mocker, sample_translation_workbook, ccli):
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    translation_sync_mock = mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationSynchronizer.sync',
        return_value=('TRN-8100-3865-4869', True),
    )
    wait_for_autotranslation_mock = mocker.patch(
        'connect.cli.plugins.translation.commands.wait_for_autotranslation',
    )
    translation_attr_sync_mock = mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationAttributesSynchronizer.sync',
    )
    runner = CliRunner()
    result = runner.invoke(ccli, ['translation', 'sync', f'{fs.root_path}/test.xlsx'])
    assert result.exit_code == 0
    translation_sync_mock.assert_called_once()
    wait_for_autotranslation_mock.assert_called_once()
    translation_attr_sync_mock.assert_called_once()


def test_sync_command_handle_input_without_xlsx(config_mocker, mocker, ccli):
    sync_open_mock = mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationSynchronizer.open',
    )
    mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationSynchronizer.sync',
        return_value=('TRN-8100-3865-4869', False),
    )
    mocker.patch('connect.cli.plugins.translation.commands.TranslationSynchronizer.save')
    mocker.patch('connect.cli.plugins.translation.commands.TranslationAttributesSynchronizer')

    runner = CliRunner()
    result = runner.invoke(ccli, ['translation', 'sync', 'TRN-8100-3865-4869'])

    assert result.exit_code == 0
    sync_open_mock.assert_called_once_with('TRN-8100-3865-4869/TRN-8100-3865-4869.xlsx')


def test_sync_command_skip_attributes_if_translation_sync_fails(config_mocker, mocker, ccli):
    mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationSynchronizer.sync',
        return_value=(None, False),
    )
    mocker.patch('connect.cli.plugins.translation.commands.TranslationSynchronizer.open')
    mocker.patch('connect.cli.plugins.translation.commands.TranslationSynchronizer.save')
    attr_sync_mock = mocker.patch(
        'connect.cli.plugins.translation.commands.TranslationAttributesSynchronizer',
    )

    runner = CliRunner()
    result = runner.invoke(ccli, ['translation', 'sync', 'TRN-8100-3865-4869'])

    assert result.exit_code == 0
    attr_sync_mock.assert_not_called()
