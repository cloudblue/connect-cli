import click
import pytest

from connect.client import ConnectClient
from connect.cli.plugins.shared.utils import wait_for_autotranslation
from connect.cli.plugins.shared.utils import (
    get_col_limit_by_ws_type,
    get_translation_attributes_sheets,
    get_ws_type_by_worksheet_name,
)

# This tests exists just to have them on code coverage, real test depends on sync action


def test_get_col_limit_unknown_type():
    assert 'Z' == get_col_limit_by_ws_type('UNKNOWN')


def test_get_ws_type_by_worksheet():
    assert 'items' == get_ws_type_by_worksheet_name('Items')
    assert 'params' == get_ws_type_by_worksheet_name('Ordering Parameters')
    assert 'params' == get_ws_type_by_worksheet_name('Fulfillment Parameters')
    assert 'params' == get_ws_type_by_worksheet_name('Configuration Parameters')
    assert 'media' == get_ws_type_by_worksheet_name('Media')
    assert 'capabilities' == get_ws_type_by_worksheet_name('Capabilities')
    assert 'static_links' == get_ws_type_by_worksheet_name('Embedding Static Resources')
    assert 'templates' == get_ws_type_by_worksheet_name('Templates')
    assert 'configurations' == get_ws_type_by_worksheet_name('Configuration')
    assert 'actions' == get_ws_type_by_worksheet_name('Actions')
    assert 'translations' == get_ws_type_by_worksheet_name('Translations')
    assert get_ws_type_by_worksheet_name('CUSTOM') is None


def test_get_translation_attributes_sheets():
    sheetnames = get_translation_attributes_sheets('./tests/fixtures/translations_sync.xlsx')

    assert sheetnames == ['FA (TRN-1079-0833-9890)', 'ES (TRN-1079-0833-9891)']


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )


def test_wait_for_autotranslation_ok(mocker, mocked_responses, mocked_translation_response):
    mocked_translation_response['auto']['status'] = 'on'
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    client = get_client()

    try:
        wait_for_autotranslation(client, mocker.MagicMock(), 'TRN-8100-3865-4869', wait_seconds=0.001)
    except Exception as e:
        pytest.fail(f'Unexpected error: {str(e)}')


@pytest.mark.parametrize('wait_response_auto,expected_error_msg', [
    (
        {'status': 'processing'},
        "Timeout waiting for pending translation tasks",
    ), (
        {'status': 'error', 'error_message': 'The auto-translation service failed'},
        "The auto-translation task failed with error: The auto-translation service failed",
    ), (
        {'status': 'unknown_status'},
        "Unknown auto-translation status: unknown_status",
    ),
])
def test_update_wait_autotranslate_fails(
    mocker, mocked_responses, mocked_translation_response, wait_response_auto, expected_error_msg,
):
    mocked_translation_response['auto'] = wait_response_auto
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    client = get_client()

    with pytest.raises(click.ClickException) as e:
        wait_for_autotranslation(client, mocker.MagicMock(), 'TRN-8100-3865-4869', wait_seconds=0.001)

    assert str(e.value) == expected_error_msg


def test_update_wait_autotranslate_error(mocker, mocked_responses, mocked_translation_response):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        status=500,
    )
    client = get_client()

    with pytest.raises(click.ClickException) as e:
        wait_for_autotranslation(client, mocker.MagicMock(), 'TRN-8100-3865-4869', wait_seconds=0.001)

    assert str(e.value) == "500 - Internal Server Error: unexpected error."
