import os
import platform
from http import HTTPStatus

import click
from connect.client import ClientError, RequestLogger as _RequestLogger

from connect.cli import get_version
from connect.cli.core.terminal import console


def get_user_agent():
    version = get_version()
    pimpl = platform.python_implementation()
    pver = platform.python_version()
    sysname = platform.system()
    sysver = platform.release()
    ua = f'connect-cli/{version} {pimpl}/{pver} {sysname}/{sysver}'
    return {'User-Agent': ua}


def format_http_status(status_code):
    status = HTTPStatus(status_code)
    description = status.name.replace('_', ' ').title()
    return f'{status_code} - {description}'


def handle_http_error(res: ClientError):
    status = format_http_status(res.status_code)

    if res.status_code in (401, 403):
        raise click.ClickException(f'{status}: please check your credentials.')

    if res.status_code == 400:
        code = res.error_code if res.error_code else 'Generic error'
        message = ','.join(res.errors) if res.errors else ''
        raise click.ClickException(f'{status}: {code} - {message}')

    raise click.ClickException(f'{status}: unexpected error.')


class RequestLogger(_RequestLogger):
    def __init__(self):
        if not console.verbose or console.silent:
            super().__init__(file=open(os.devnull, 'w'))
        else:
            super().__init__(file=None)
