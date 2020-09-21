import json

from click.testing import CliRunner

from cnctcli.ccli import cli
from cnctcli.config import Account
from cnctcli.constants import DEFAULT_ENDPOINT

from tests.data import CONFIG_DATA


def test_add_account(mocker):
    mock = mocker.patch(
        'cnctcli.commands.account.add_account',
        return_value=('VA-000', 'Account 0'),
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
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


def test_add_account_custom_endpoint(mocker):
    mock = mocker.patch(
        'cnctcli.commands.account.add_account',
        return_value=('VA-000', 'Account 0'),
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'account',
            'add',
            'ApiKey XXX:YYY',
            '--endpoint',
            'https://custom_endpoint'
        ],
    )
    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'ApiKey XXX:YYY'
    assert mock.mock_calls[0][1][2] == 'https://custom_endpoint'
    assert result.output == 'New account added: VA-000 - Account 0\n'


def test_remove_account(mocker):
    mock = mocker.patch(
        'cnctcli.commands.account.remove_account',
        side_effect=lambda *args: Account('VA-000', 'Account 0', '', ''),
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'account',
            'remove',
            'VA-000',
        ],
    )

    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'VA-000'
    assert result.output == 'Account removed: VA-000 - Account 0\n'


def test_activate_account(mocker):
    mock = mocker.patch(
        'cnctcli.commands.account.activate_account',
        side_effect=lambda *args: Account('VA-000', 'Account 0', '', ''),
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'account',
            'activate',
            'VA-000',
        ],
    )

    assert result.exit_code == 0
    assert mock.mock_calls[0][1][1] == 'VA-000'
    assert result.output == 'Current active account is: VA-000 - Account 0\n'


def test_list_accounts(mocker):
    mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )
    mocker.patch('os.path.isfile', return_value=True)

    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            'account',
            'list',
        ],
    )

    assert result.exit_code == 0
    assert result.output == (
        'VA-000 - Account 0 (active)\n'
        'VA-001 - Account 1\n'
    )
