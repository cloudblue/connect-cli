import click
import pytest

from connect.client import ConnectClient
from connect.cli.plugins.shared.utils import wait_for_autotranslation


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )


def test_wait_for_autotranslation_ok(mocked_responses, mocked_translation_response):
    mocked_translation_response['auto']['status'] = 'on'
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    client = get_client()

    try:
        wait_for_autotranslation(client, 'TRN-8100-3865-4869', wait_seconds=0.001, silent=True)
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
    mocked_responses, mocked_translation_response, wait_response_auto, expected_error_msg,
):
    mocked_translation_response['auto'] = wait_response_auto
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    client = get_client()

    with pytest.raises(click.ClickException) as e:
        wait_for_autotranslation(client, 'TRN-8100-3865-4869', wait_seconds=0.001, silent=True)

    assert str(e.value) == expected_error_msg


def test_update_wait_autotranslate_error(mocked_responses, mocked_translation_response):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869',
        status=500,
    )
    client = get_client()

    with pytest.raises(click.ClickException) as e:
        wait_for_autotranslation(client, 'TRN-8100-3865-4869', wait_seconds=0.001, silent=True)

    assert str(e.value) == "500 - Internal Server Error: unexpected error."
