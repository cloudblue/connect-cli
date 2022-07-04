import click
import pytest

from connect.client import ConnectClient
from connect.cli.plugins.translation.activate import activate_translation


def test_activate_translation(
    mocked_responses,
    mocked_translation_response,
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/activate',
        json=mocked_translation_response,
        status=200,
    )

    translation = activate_translation(
        ConnectClient(
            'ApiKey XXX',
            endpoint='https://localhost/public/v1',
            use_specs=False,
        ),
        translation_id='TRN-8100-3865-4869',
    )

    assert translation['status'] == 'active'


def test_translation_already_activated(mocked_responses):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/activate',
        json={
            "error_code": "TRE_003",
            "errors": [
                "This translation is already activated.",
            ],
        },
        status=400,
    )

    with pytest.raises(click.ClickException) as e:
        activate_translation(
            ConnectClient(
                'ApiKey XXX',
                endpoint='https://localhost/public/v1',
                use_specs=False,
            ),
            translation_id='TRN-8100-3865-4869',
        )

    assert str(e.value) == '400 - Bad Request: TRE_003 - This translation is already activated.'


def test_activate_translation_not_exists(mocked_responses):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-0000-0000-0000/activate',
        status=404,
    )
    with pytest.raises(click.ClickException) as e:
        activate_translation(
            ConnectClient(
                'ApiKey XXX',
                endpoint='https://localhost/public/v1',
                use_specs=False,
            ),
            translation_id='TRN-0000-0000-0000',
        )
    assert str(e.value) == '404 - Not Found: Translation TRN-0000-0000-0000 not found.'
