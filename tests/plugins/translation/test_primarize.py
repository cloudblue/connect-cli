import click
import pytest

from connect.cli.plugins.translation.primarize import primarize_translation


def test_primarize_translation(
    mocked_responses,
    mocked_translation_response,
):
    mocked_translation_response['primary'] = True
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/primarize',
        json=mocked_translation_response,
        status=200,
    )

    translation = primarize_translation(
        api_url='https://localhost/public/v1',
        api_key='ApiKey XXX',
        translation_id='TRN-8100-3865-4869',
    )

    assert translation['primary']


def test_translation_already_primary(mocked_responses):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/primarize',
        json={
            "error_code": "TRE_005",
            "errors": [
                "This translation is already a primary translation.",
            ],
        },
        status=400,
    )

    with pytest.raises(click.ClickException) as e:
        primarize_translation(
            api_url='https://localhost/public/v1',
            api_key='ApiKey XXX',
            translation_id='TRN-8100-3865-4869',
        )

    assert str(e.value) == '400 - Bad Request: TRE_005 - This translation is already a primary translation.'


def test_primarize_translation_not_exists(mocked_responses):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/localization/translations/TRN-0000-0000-0000/primarize',
        status=404,
    )
    with pytest.raises(click.ClickException) as e:
        primarize_translation(
            api_url='https://localhost/public/v1',
            api_key='ApiKey XXX',
            translation_id='TRN-0000-0000-0000',
        )
    assert str(e.value) == '404 - Not Found: Translation TRN-0000-0000-0000 not found.'
