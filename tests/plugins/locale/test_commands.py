from click.testing import CliRunner


def test_list_locales(config_mocker, mocked_responses, mocked_locales_response, ccli):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/localization/locales',
        headers={
            'Content-Range': 'items 0-0/1',
        },
        json=[
            {
                "id": "EN-AU",
                "name": "Australian English",
                "local_name": "Australian English",
                "auto_translation": False,
                "stats": {
                    "translations": 0,
                },
            },
        ],
    )
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'locale',
            'list',
        ],
    )
    assert result.exit_code == 0
    assert 'Current active account: VA-000 - Account 0' in result.output
    assert '│ EN-AU │ Australian English │        ✖        │      -       │' in result.output


def test_list_with_page_size_less_than_zero(config_mocker, ccli):
    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            '-p',
            '-1',
            'locale',
            'list',
        ],
    )
    assert result.exit_code == 2
    assert "Error: Invalid value for '--page-size' / '-p': -1 is not in the range x>=1." in result.output
