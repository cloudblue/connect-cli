# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click
import requests


from cnctcli.api.utils import (
    format_http_status,
    get_headers,
    handle_http_error,
)


def get_units(endpoint, api_key):
    results = []

    has_more = True
    limit = 100
    offset = 0

    while has_more:
        res = requests.get(
            f'{endpoint}/settings/units',
            params={'limit': limit, 'offset': offset},
            headers=get_headers(api_key),
        )
        if res.status_code == 200:
            page = res.json()
            results.extend(page)
            has_more = len(page) == 100
            continue
        handle_http_error(res)
    return results


def create_unit(endpoint, api_key, data):
    res = requests.post(
        f'{endpoint}/settings/units',
        headers=get_headers(api_key),
        json=data,
    )
    if res.status_code == 201:
        return res.json()

    handle_http_error(res)


def get_products(endpoint, api_key, query, limit, offset):
    url = f'{endpoint}/products'
    if query:
        url = f'{url}?{query}'
    res = requests.get(
        f'{endpoint}/products',
        params={'limit': limit, 'offset': offset},
        headers=get_headers(api_key),
    )
    if res.status_code == 200:
        return res.json()

    handle_http_error(res)


def get_product(endpoint, api_key, product_id):
    res = requests.get(
        f'{endpoint}/products/{product_id}',
        headers=get_headers(api_key),
    )

    if res.status_code == 200:
        return res.json()

    status = format_http_status(res.status_code)

    if res.status_code == 404:
        raise click.ClickException(f'{status}: Product {product_id} not found.')

    handle_http_error(res)


def get_items(endpoint, api_key, product_id, limit=100, offset=0):

    res = requests.get(
        f'{endpoint}/products/{product_id}/items',
        params={'limit': limit, 'offset': offset},
        headers=get_headers(api_key),
    )

    if res.status_code == 200:
        header = res.headers['Content-Range']
        count = int(header.rsplit('/', 1)[-1])
        return count, res.json()

    status = format_http_status(res.status_code)

    if res.status_code == 404:
        raise click.ClickException(f'{status}: Product {product_id} not found.')

    handle_http_error(res)


def get_item(endpoint, api_key, product_id, item_id):
    res = requests.get(
        f'{endpoint}/products/{product_id}/items/{item_id}',
        headers=get_headers(api_key),
    )

    if res.status_code == 200:
        return res.json()

    if res.status_code == 404:
        return

    handle_http_error(res)


def get_item_by_mpn(endpoint, api_key, product_id, mpn):
    res = requests.get(
        f'{endpoint}/products/{product_id}/items?eq(mpn,{mpn})',
        headers=get_headers(api_key),
    )

    if res.status_code == 200:
        results = res.json()
        return results[0] if results else None

    if res.status_code == 404:
        return

    handle_http_error(res)


def create_item(endpoint, api_key, product_id, data):
    res = requests.post(
        f'{endpoint}/products/{product_id}/items',
        headers=get_headers(api_key),
        json=data,
    )
    if res.status_code == 201:
        return res.json()

    handle_http_error(res)


def update_item(endpoint, api_key, product_id, item_id, data):
    res = requests.put(
        f'{endpoint}/products/{product_id}/items/{item_id}',
        headers=get_headers(api_key),
        json=data,
    )
    if res.status_code != 200:
        handle_http_error(res)

    return res.json()


def delete_item(endpoint, api_key, product_id, item_id):
    res = requests.delete(
        f'{endpoint}/products/{product_id}/items/{item_id}',
        headers=get_headers(api_key),
    )
    if res.status_code != 204:
        handle_http_error(res)
