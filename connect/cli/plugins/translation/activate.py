import click
from connect.client import ClientError

from connect.cli.core.http import format_http_status, handle_http_error


def activate_translation(client, translation_id):
    try:
        payload = {
            'status': 'active',
        }
        translation = (
            client.ns('localization')
            .translations[translation_id]
            .action('activate')
            .post(payload=payload)
        )
    except ClientError as error:
        if error.status_code == 404:
            status = format_http_status(error.status_code)
            raise click.ClickException(f'{status}: Translation {translation_id} not found.')
        handle_http_error(error)
    return translation
