import platform

import pytest

from click import ClickException

from cnctcli import get_version
from cnctcli.api.utils import (
    format_http_status,
    get_headers,
    handle_http_error,
)


def test_get_headers():
    headers = get_headers('MY API KEY')

    assert 'Authorization' in headers
    assert headers['Authorization'] == 'MY API KEY'
    assert 'User-Agent' in headers

    ua = headers['User-Agent']

    cli, python, system = ua.split()

    assert cli == f'connect-cli/{get_version()}'
    assert python == f'{platform.python_implementation()}/{platform.python_version()}'
    assert system == f'{platform.system()}/{platform.release()}'


def test_format_http_status():
    assert format_http_status(401) == '401 - Unauthorized'
    assert format_http_status(404) == '404 - Not Found'
    assert format_http_status(500) == '500 - Internal Server Error'

    with pytest.raises(Exception):
        format_http_status(1)


def test_handle_http_error_400(mocker):
    res = mocker.MagicMock()
    res.status_code = 400
    res.json = lambda: {'error_code': 'SYS-000', 'errors': ['error1', 'error2']}

    with pytest.raises(ClickException) as e:
        handle_http_error(res)

    assert str(e.value) == '400 - Bad Request: SYS-000 - error1,error2'


@pytest.mark.parametrize(
    ('code', 'description', 'message'),
    (
        (401, 'Unauthorized', 'please check your credentials.'),
        (403, 'Forbidden', 'please check your credentials.'),
        (500, 'Internal Server Error', 'unexpected error.'),
        (502, 'Bad Gateway', 'unexpected error.'),
    )
)
def test_handle_http_error_others(mocker, code, description, message):
    res = mocker.MagicMock()
    res.status_code = code

    with pytest.raises(ClickException) as e:
        handle_http_error(res)

    assert str(e.value) == f'{code} - {description}: {message}'
