# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import click

from connect.client import ClientError, ConnectClient
from connect.cli.core.http import RequestLogger


def add_account(config, api_key, endpoint):
    try:
        client = ConnectClient(
            api_key=api_key,
            endpoint=endpoint,
            validate_using_specs=False,
            use_specs=False,
            logger=RequestLogger(),
        )
        account_data = client.accounts.all().first()
        config.add_account(
            account_data['id'],
            account_data['name'],
            api_key,
            endpoint,
        )
        config.store()
        return account_data['id'], account_data['name']

    except ClientError as h:
        msg = f'Unexpected error: {h}'
        if h.status_code == 401:
            msg = 'Unauthorized: the provided api key is invalid.'
        raise click.ClickException(msg)


def activate_account(config, id):
    config.activate(id)
    config.store()
    return config.active


def remove_account(config, id):
    acc = config.remove_account(id)
    config.store()
    return acc
