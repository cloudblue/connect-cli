# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from time import sleep

import click
from tqdm import trange

from connect.client import ClientError
from connect.cli.core.http import handle_http_error
from connect.cli.core.constants import DEFAULT_BAR_FORMAT


def wait_for_autotranslation(client, translation_id, wait_seconds=1, max_counts=5, silent=False):
    progress = trange(0, max_counts, disable=silent, leave=False, bar_format=DEFAULT_BAR_FORMAT)
    for _ in progress:
        progress.set_description('Waiting for pending translation tasks')
        sleep(wait_seconds)
        try:
            translation = client.ns('localization').translations[translation_id].get()
        except ClientError as error:
            handle_http_error(error)
        status = translation['auto']['status']
        if status == 'processing':
            pass
        elif status in ('on', 'off'):
            break
        elif status == 'error':
            translation['auto']['error_message']
            raise click.ClickException(
                'The auto-translation task failed with error: '
                + translation['auto']['error_message'],
            )
        else:
            raise click.ClickException(f'Unknown auto-translation status: {status}')
    else:
        raise click.ClickException('Timeout waiting for pending translation tasks')
