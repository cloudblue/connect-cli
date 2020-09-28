# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click
import requests


def add_account(config, api_key, endpoint):
    headers = {
        'Authorization': api_key,
    }

    res = requests.get(f'{endpoint}/accounts', headers=headers)
    if res.status_code == 401:
        raise click.ClickException('Unauthorized: the provided api key is invalid.')

    if res.status_code == 200:
        account_data = res.json()[0]
        account_id = account_data['id']
        name = account_data['name']
        config.add_account(
            account_id,
            name,
            api_key,
            endpoint,
        )
        config.store()
        return account_id, name

    raise click.ClickException(f'Unexpected error: {res.status_code} - {res.text}')


def activate_account(config, id):
    config.activate(id)
    config.store()
    return config.active


def remove_account(config, id):
    acc = config.remove_account(id)
    config.store()
    return acc
