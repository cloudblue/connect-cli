import pytest
from click import ClickException

from connect.cli.plugins.project.extension.constants import PYPI_EXTENSION_RUNNER_URL
from connect.cli.plugins.project.extension.utils import (
    check_extension_events_applicable,
    check_extension_interactive_events_applicable,
    check_extension_not_multi_account,
    check_webapp_feature_not_selected,
    get_background_events,
    get_event_definitions,
    get_interactive_events,
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


def test_get_background_events():
    context = {'extension_type': 'products'}
    definitions = {
        'miltiaccount': {},
        'products': {
            'background': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
        },
    }

    res = get_background_events(definitions, context)

    assert len(res) == 2
    assert ('Type1', 'Group1: Name1') in res


def test_get_interactive_events():
    context = {'extension_type': 'products'}
    definitions = {
        'miltiaccount': {},
        'products': {
            'interactive': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
        },
    }

    res = get_interactive_events(definitions, context)

    assert len(res) == 2
    assert ('Type1', 'Group1: Name1') in res


def test_check_extension_not_multi_account():
    data = {'extension_type': 'multiaccount'}
    assert check_extension_not_multi_account(data) is False


def test_check_extension_events_applicable_false():
    context = {'extension_type': 'products'}

    assert check_extension_events_applicable(context) is False


def test_check_extension_events_applicable_true():
    context = {'extension_type': 'multiaccount', 'application_types': ['anvil']}

    assert check_extension_events_applicable(context) is True


def test_check_extension_interactive_events_applicable_false():
    context = {'extension_type': 'products'}
    definitions = {
        'multiaccount': {
            'background': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
        },
    }
    assert check_extension_interactive_events_applicable(definitions, context) is False


def test_check_extension_interactive_events_applicable_true():
    context = {'extension_type': 'multiaccount', 'application_types': ['anvil']}
    definitions = {
        'multiaccount': {
            'background': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
        },
    }
    assert check_extension_interactive_events_applicable(definitions, context) is True


@pytest.mark.parametrize(
    ('app_types', 'expected'),
    (
        (['webapp'], False),
        ([], True),
    ),
)
def test_check_webapp_feature_not_selected(app_types, expected):
    assert check_webapp_feature_not_selected({'application_types': app_types}) is expected
