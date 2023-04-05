import pytest
from click import ClickException
from connect.client import ClientError

from connect.cli.plugins.project.extension.constants import PYPI_EXTENSION_RUNNER_URL
from connect.cli.plugins.project.extension.utils import (
    check_eventsapp_feature_not_selected,
    check_extension_events_applicable,
    check_extension_not_multi_account,
    check_webapp_feature_not_selected,
    get_application_types,
    get_available_event_types,
    get_background_events,
    get_default_application_types,
    get_event_definitions,
    get_interactive_events,
    get_pypi_runner_version,
)


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
    context = {'extension_type': 'products', 'application_types': ['events']}

    assert check_extension_events_applicable(context) is False


def test_check_extension_events_applicable_true():
    context = {'extension_type': 'multiaccount', 'application_types': ['anvil']}

    assert check_extension_events_applicable(context) is True


def test_get_available_event_types_full():
    context = {
        'extension_type': 'multiaccount',
        'event_types': ['interactive'],
        'application_types': ['anvil'],
    }
    definitions = {
        'multiaccount': {
            'background': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
            'interactive': [
                {'type': 'Type3', 'group': 'Group3', 'name': 'Name3'},
            ],
        },
    }

    event_types = get_available_event_types(definitions, context)
    assert len(event_types) == 3
    assert ('background', 'Background Events') in event_types
    assert ('interactive', 'Interactive Events') in event_types
    assert ('scheduled', 'Scheduled Event Example') in event_types


def test_get_available_event_types_full_no_background():
    context = {
        'extension_type': 'multiaccount',
        'event_types': ['interactive'],
        'application_types': ['anvil'],
    }
    definitions = {
        'multiaccount': {
            'interactive': [
                {'type': 'Type3', 'group': 'Group3', 'name': 'Name3'},
            ],
        },
    }

    event_types = get_available_event_types(definitions, context)
    assert len(event_types) == 2
    assert ('interactive', 'Interactive Events') in event_types
    assert ('scheduled', 'Scheduled Event Example') in event_types


def test_get_available_event_types_full_no_interactive():
    context = {
        'extension_type': 'multiaccount',
        'event_types': ['background', 'interactive'],
        'application_types': ['anvil'],
    }
    definitions = {
        'multiaccount': {
            'background': [
                {'type': 'Type1', 'group': 'Group1', 'name': 'Name1'},
                {'type': 'Type2', 'group': 'Group2', 'name': 'Name2'},
            ],
        },
    }

    res = get_available_event_types(definitions, context)
    assert len(res) == 2

    assert ('background', 'Background Events') in res
    assert ('scheduled', 'Scheduled Event Example') in res


@pytest.mark.parametrize(
    ('app_types', 'extension_type', 'expected'),
    (
        (['webapp'], 'multiaccount', False),
        (['webapp'], 'products', True),
        (['webapp'], 'hub', True),
        ([], 'multiaccount', True),
        ([], 'products', True),
        ([], 'hub', True),
    ),
)
def test_check_webapp_feature_not_selected(app_types, extension_type, expected):
    assert check_webapp_feature_not_selected({
        'application_types': app_types,
        'extension_type': extension_type,
    }) is expected


@pytest.mark.parametrize(
    ('app_types', 'expected'),
    (
        (['events'], False),
        ([], True),
    ),
)
def test_check_eventsapp_feature_not_selected(app_types, expected):
    assert check_eventsapp_feature_not_selected({'application_types': app_types}) is expected


def test_get_application_types():
    context = {'extension_type': 'products'}
    single_tenant = get_application_types(context)

    context['extension_type'] = 'multiaccount'
    multi_tenant = get_application_types(context)

    context['extension_type'] = 'transformations'
    transformations = get_application_types(context)

    assert len(single_tenant) == 2
    assert ('webapp', 'Web Application') not in single_tenant

    assert len(multi_tenant) == 3
    assert ('webapp', 'Web Application') in multi_tenant

    assert len(multi_tenant) == 3
    assert ('webapp', 'Web Application') in transformations
    assert ('tfnapp', 'Transformations Application') in transformations


def test_get_default_application_types():
    context = {'extension_type': 'transformations'}
    tfnapp = get_default_application_types(context)

    context['extension_type'] = 'multiaccount'
    multi_tenant = get_default_application_types(context)

    assert tfnapp == ['webapp', 'tfnapp']
    assert multi_tenant == []
