import platform
from http import HTTPStatus

import click

from cnctcli import get_version


def _get_user_agent():
    version = get_version()
    pimpl = platform.python_implementation()
    pver = platform.python_version()
    sysname = platform.system()
    sysver = platform.release()
    ua = f'connect-cli/{version} {pimpl}/{pver} {sysname}/{sysver}'
    return {'User-Agent': ua}


def get_headers(api_key):
    headers = {'Authorization': api_key}
    headers.update(_get_user_agent())
    return headers


def format_http_status(status_code):
    status = HTTPStatus(status_code)
    description = status.name.replace('_', ' ').title()
    return f'{status_code} - {description}'


def handle_http_error(res):
    status = format_http_status(res.status_code)

    if res.status_code in (401, 403):
        raise click.ClickException(f'{status}: please check your credentials.')

    if res.status_code == 400:
        error_info = res.json()
        code = error_info['error_code']
        message = ','.join(error_info['errors'])
        raise click.ClickException(f'{status}: {code} - {message}')

    raise click.ClickException(f'{status}: unexpected error.')
