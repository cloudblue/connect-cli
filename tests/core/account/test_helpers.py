import pytest

import click

from connect.cli.core.account.helpers import (
    activate_account,
    add_account,
    remove_account,
)
from connect.cli.core.config import Config


def test_add_account(mocker, mocked_responses):
    config = Config()
    config.add_account = mocker.MagicMock()
    config.store = mocker.MagicMock()
    mocked_responses.add(
        'GET',
        'https://localhost/public/v1/accounts',
        status=200,
        json=[{'id': 'VA-000', 'name': 'Test account'}],
    )
    acc_id, acc_name = add_account(config, 'api_key', 'https://localhost/public/v1')
    config.add_account.assert_called_once_with(
        'VA-000', 'Test account',
        'api_key', 'https://localhost/public/v1',
    )
    assert acc_id == 'VA-000'
    assert acc_name == 'Test account'
    config.store.assert_called()


def test_add_account_invalid_api_key(mocked_responses):
    config = Config()
    mocked_responses.add(
        'GET',
        'https://localhost/public/v1/accounts',
        status=401,
        json={
            "error_code": "AUTH_001",
            "errors": [
                "API request is unauthorized.",
            ],
        },
    )

    with pytest.raises(click.ClickException) as ex:
        add_account(
            config,
            'ApiKey SU-000:xxxx',
            'https://localhost/public/v1',
        )
    assert ex.value.message == 'Unauthorized: the provided api key is invalid.'


def test_add_account_internal_server_error(mocked_responses):
    config = Config()
    mocked_responses.add(
        'GET',
        'https://localhost/public/v1/accounts',
        status=500,
        body=b'Internal Server Error',
    )

    with pytest.raises(click.ClickException) as ex:
        add_account(
            config,
            'ApiKey SU-000:xxxx',
            'https://localhost/public/v1',
        )
    assert ex.value.message == 'Unexpected error: 500 Internal Server Error'


def test_activate_account(mocker):
    mock = mocker.patch.object(Config, 'store')
    config = Config()
    config.add_account('VA-000', 'Account 0', 'Api 0')
    config.add_account('VA-001', 'Account 1', 'Api 1')

    assert config.active.id == 'VA-000'

    acc = activate_account(config, 'VA-001')

    assert acc.id == 'VA-001'
    assert config.active.id == 'VA-001'
    mock.assert_called_once()


def test_remove_account(mocker):
    mock = mocker.patch.object(Config, 'store')
    config = Config()
    config.add_account('VA-000', 'Account 0', 'Api 0')
    config.add_account('VA-001', 'Account 1', 'Api 1')

    assert config.active.id == 'VA-000'

    acc = remove_account(config, 'VA-000')

    assert acc.id == 'VA-000'
    assert config.active.id == 'VA-001'
    mock.assert_called_once()
