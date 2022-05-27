import json

import click
import pytest

from connect.cli.core.config import Config
from connect.cli.core.constants import DEFAULT_ENDPOINT


def test_load(config_mocker, mocker):
    config = Config()
    config.load('/tmp')
    assert config.active is not None
    assert config.active.id == 'VA-000'
    assert len(config.accounts) == 2


def test_store(mocker):
    mock_open = mocker.mock_open()
    mocker.patch(
        'connect.cli.core.config.open',
        mock_open,
    )

    config = Config()
    config._config_path = '/tmp'
    config.add_account('VA-000', 'Account 1', 'ApiKey XXXX:YYYY')

    config.store()
    assert mock_open.mock_calls[0][1][1] == 'w'
    expected_output = {
        'active': 'VA-000',
        'accounts': [
            {
                'id': 'VA-000',
                'name': 'Account 1',
                'api_key': 'ApiKey XXXX:YYYY',
                'endpoint': DEFAULT_ENDPOINT,
            },
        ],
    }
    assert json.loads(mock_open.mock_calls[2][1][0]) == expected_output


def test_add_account():
    config = Config()
    config.add_account('VA-000', 'Account 1', 'ApiKey XXXX:YYYY')

    assert config.active is not None
    assert config.active.id == 'VA-000'
    assert config.active.name == 'Account 1'
    assert config.active.api_key == 'ApiKey XXXX:YYYY'
    assert config.active.endpoint == DEFAULT_ENDPOINT


def test_add_account_custom_endpoint():
    config = Config()
    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://my_custom_endpoint',
    )

    assert config.active.endpoint == 'https://my_custom_endpoint'


def test_activate(config_mocker, mocker):
    config = Config()
    config.load('/tmp')

    assert config.active.id == 'VA-000'

    config.activate('VA-001')

    assert config.active is not None
    assert config.active.id == 'VA-001'
    assert config.active.name == 'Account 1'
    assert config.active.api_key == 'ApiKey ZZZZ:SSSS'


def test_activate_non_existent_account():
    config = Config()

    with pytest.raises(click.ClickException) as ex:
        config.activate('VA-999')

    assert ex.value.message == 'The account identified by VA-999 does not exist.'


def test_remove_account():
    config = Config()

    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://my_custom_endpoint',
    )

    assert config.active.id == 'VA-000'
    assert len(config.accounts) == 1

    config.remove_account('VA-000')

    assert config.active is None
    assert len(config.accounts) == 0


def test_remove_non_existent_account():
    config = Config()
    with pytest.raises(click.ClickException) as ex:
        config.remove_account('VA-999')

    assert ex.value.message == 'The account identified by VA-999 does not exist.'


def test_remove_activate_other(config_mocker, mocker):
    config = Config()
    config.load('/tmp')

    assert config.active.id == 'VA-000'

    config.remove_account('VA-000')

    assert config.active.id == 'VA-001'


def test_remove_non_active_account():
    config = Config()

    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://my_custom_endpoint',
    )

    config.add_account(
        'VA-001',
        'Account 2',
        'ApiKey XXXX:YYYY',
        endpoint='https://my_custom_endpoint',
    )

    assert config.active.id == 'VA-000'
    assert len(config.accounts) == 2

    config.remove_account('VA-001')

    assert config.active.id == 'VA-000'
    assert len(config.accounts) == 1


def test_config_validate():
    config = Config()

    with pytest.raises(click.ClickException) as ex:
        config.validate()

    assert ex.value.message == (
        'connect-cli is not properly configured.\n'
        'You must configure at least a Connect account. To do so please execute:\n\n'
        'ccli account add API_KEY\n\n'
    )

    config.add_account(
        'VA-000',
        'Account 1',
        'ApiKey XXXX:YYYY',
        endpoint='https://my_custom_endpoint',
    )

    assert config.validate() is None
