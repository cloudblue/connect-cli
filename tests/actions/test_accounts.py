import pytest

import click

from cnctcli.actions.accounts import (
    activate_account,
    add_account,
    remove_account,
)
from cnctcli.config import Config


def test_add_account_invalid_api_key(requests_mock):
    config = Config()
    requests_mock.get(
        'https://localhost/public/v1/accounts',
        status_code=401,
        json={
            "error_code": "AUTH_001",
            "errors": [
                "API request is unauthorized."
            ]
        }
    )

    with pytest.raises(click.ClickException) as ex:
        add_account(
            config,
            'ApiKey SU-000:xxxx',
            'https://localhost/public/v1',
        )
    assert ex.value.message == 'Unauthorized: the provided api key is invalid.'


def add_account_internal_server_error(requests_mock):
    config = Config()
    requests_mock.get(
        'https://localhost/public/v1/accounts',
        status_code=500,
        text='Internal Server Error'
    )

    with pytest.raises(click.ClickException) as ex:
        add_account(
            config,
            'ApiKey SU-000:xxxx',
            'https://localhost/public/v1',
        )
    assert ex.value.message == 'Unexpected error: 500 - Internal Server Error'


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
