import platform

import pytest
from click import ClickException
from connect.client import ClientError

from connect.cli import get_version
from connect.cli.core.http import (
    RequestLogger,
    format_http_status,
    get_user_agent,
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
    ),
)
def test_handle_http_error_others(mocker, code, description, message):
    res = mocker.MagicMock()
    res.status_code = code

    with pytest.raises(ClickException) as e:
        handle_http_error(res)

    assert str(e.value) == f'{code} - {description}: {message}'


def test_get_user_agent():
    user_agent_header = get_user_agent()
    ua = user_agent_header['User-Agent']

    cli, python, system = ua.split()
    assert cli == f'connect-cli/{get_version()}'
    assert python == f'{platform.python_implementation()}/{platform.python_version()}'
    assert system == f'{platform.system()}/{platform.release()}'


def test_request_logger_creation(mocker):
    mocker.patch('connect.cli.core.http.console')
    req_logger = RequestLogger()
    assert req_logger._file is not None


def test_request_logger_creation_empty(mocker):
    mocked_console = mocker.MagicMock()
    mocked_console.verbose = True
    mocked_console.silent = False
    mocker.patch('connect.cli.core.http.console', mocked_console)
    req_logger = RequestLogger()
    assert req_logger._file is None
