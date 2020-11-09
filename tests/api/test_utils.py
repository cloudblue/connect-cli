import platform

import pytest

from click import ClickException
from cnct import ClientError
from cnctcli.api.utils import (
    format_http_status,
    handle_http_error,
)


def test_format_http_status():
    assert format_http_status(401) == '401 - Unauthorized'
    assert format_http_status(404) == '404 - Not Found'
    assert format_http_status(500) == '500 - Internal Server Error'

    with pytest.raises(Exception):
        format_http_status(1)


def test_handle_http_error_400(mocker):
    res = ClientError()
    res.status_code = 400
    res.errors = ['error1', 'error2']
    res.error_code = 'SYS-000'
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
