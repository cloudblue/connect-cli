import pytest
from click import ClickException

from connect.cli.plugins.project.extension.constants import PYPI_EXTENSION_RUNNER_URL
from connect.cli.plugins.project.extension.utils import (
    check_extension_not_events_application,
    check_extension_not_hub,
    check_extension_not_multi_account,
    check_extension_not_products,
    get_event_definitions,
    get_pypi_runner_version,
)
from connect.client import ClientError


def test_get_pypi_runner_version(mocker, mocked_responses):
    mocker.patch(
        'connect.cli.plugins.project.extension.utils.get_version',
        return_value='25.0',
    )
    mocked_responses.add(
        method='GET',
        url=PYPI_EXTENSION_RUNNER_URL,
        json={
            'releases': {
                '26.0': {},
                '25.1': {},
                '25.0': {},
                '24.5': {},
            },
        },
        status=200,
    )

    assert get_pypi_runner_version() == '25.1'


def test_get_pypi_runner_version_http_error(mocker, mocked_responses):
    mocker.patch(
        'connect.cli.plugins.project.extension.utils.get_version',
        return_value='25.0',
    )
    mocked_responses.add(
        method='GET',
        url=PYPI_EXTENSION_RUNNER_URL,
        status=500,
    )
    with pytest.raises(ClickException) as ve:
        get_pypi_runner_version()

    assert 'We can not retrieve the current connect-extension-runner version' in str(ve.value)


def test_get_pypi_runner_version_no_releases(mocker, mocked_responses):
    mocker.patch(
        'connect.cli.plugins.project.extension.utils.get_version',
        return_value='25.0',
    )
    mocked_responses.add(
        method='GET',
        url=PYPI_EXTENSION_RUNNER_URL,
        status=200,
        json={
            'info': {'version': '26.0'},
            'releases': {},
        },
    )

    assert get_pypi_runner_version() == '26.0'


def test_get_event_definitions_client_error(mocker):
    config = mocker.MagicMock()
    config.active.client = mocker.MagicMock(side_effect=ClientError)

    with pytest.raises(ClickException) as exc:
        get_event_definitions(config)

    assert str(exc.value) == 'Error getting event definitions: Unexpected error'


def test_check_extension_not_events_application():
    data = {
        'extension_type': 'products',
        'application_types': [],
    }

    assert check_extension_not_events_application(data) is True

    data['extension_type'] = 'multiaccount'
    data['application_types'].append('anvil')

    assert check_extension_not_events_application(data) is True

    data['application_types'].append('events')

    assert check_extension_not_events_application(data) is False


def test_check_extension_not_hub():
    data = {'extension_type': 'products'}
    assert check_extension_not_hub(data) is True

    data['extension_type'] = 'hub'
    assert check_extension_not_hub(data) is False


def test_check_extension_not_multi_account():
    data = {'extension_type': 'multiaccount'}
    assert check_extension_not_multi_account(data) is False

    data['extension_type'] = 'hub'
    assert check_extension_not_multi_account(data) is True


def test_check_extension_not_products():
    data = {'extension_type': 'products'}
    assert check_extension_not_products(data) is False

    data['extension_type'] = 'multiaccount'
    assert check_extension_not_products(data) is True
