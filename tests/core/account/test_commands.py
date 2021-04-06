from click.testing import CliRunner

from connect.cli.core.config import Account
from connect.cli.core.constants import DEFAULT_ENDPOINT


def test_add_account(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.add_account',
        return_value=('VA-000', 'Account 0'),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'account',
            'add',
            'ApiKey XXX:YYY',
        ],
    )
    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'ApiKey XXX:YYY'
    assert mock.mock_calls[0][1][2] == DEFAULT_ENDPOINT
    assert result.output == 'New account added: VA-000 - Account 0\n'


def test_add_account_silent(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.add_account',
        return_value=('VA-000', 'Account 0'),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-s',
            'account',
            'add',
            'ApiKey XXX:YYY',
        ],
    )
    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'ApiKey XXX:YYY'
    assert mock.mock_calls[0][1][2] == DEFAULT_ENDPOINT
    assert 'New account added: VA-000 - Account 0\n' not in result.output


def test_add_account_custom_endpoint(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.add_account',
        return_value=('VA-000', 'Account 0'),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'account',
            'add',
            'ApiKey XXX:YYY',
            '--endpoint',
            'https://custom_endpoint',
        ],
    )
    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'ApiKey XXX:YYY'
    assert mock.mock_calls[0][1][2] == 'https://custom_endpoint'
    assert 'New account added: VA-000 - Account 0\n' in result.output


def test_remove_account(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.remove_account',
        side_effect=lambda *args: Account('VA-000', 'Account 0', '', ''),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'account',
            'remove',
            'VA-000',
        ],
    )

    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'VA-000'
    assert 'Account removed: VA-000 - Account 0\n' in result.output


def test_activate_account(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.activate_account',
        side_effect=lambda *args: Account('VA-000', 'Account 0', '', ''),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'account',
            'activate',
            'VA-000',
        ],
    )

    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'VA-000'
    assert 'Current active account is: VA-000 - Account 0\n' in result.output


def test_activate_account_silent(mocker, ccli, config_mocker):
    mock = mocker.patch(
        'connect.cli.core.account.commands.activate_account',
        side_effect=lambda *args: Account('VA-000', 'Account 0', '', ''),
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-s',
            'account',
            'activate',
            'VA-000',
        ],
    )

    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'VA-000'
    assert 'Current active account is: VA-000 - Account 0\n' not in result.output


def test_list_accounts(config_mocker, mocker, ccli):
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'account',
            'list',
        ],
    )

    assert result.exit_code == 0
    assert '│VA-000│Account 0│  ✓   │\n│VA-001│Account 1│      │\n' in result.output
