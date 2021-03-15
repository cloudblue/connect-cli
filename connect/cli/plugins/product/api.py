# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

from connect.cli.core.http import handle_http_error
from connect.client import ClientError, R


def create_unit(client, data):
    try:
        res = client.ns('settings').units.create(data)
    except ClientError as error:
        handle_http_error(error)
    return res


def get_item(client, product_id, item_id):
    try:
        res = client.products[product_id].items[item_id].get()
    except ClientError as error:
        if error.status_code == 404:
            return
        handle_http_error(error)
    return res


def get_item_by_mpn(client, product_id, mpn):
    rql = R().mpn.eq(mpn)

    try:
        res = (
            client.products[product_id]
            .items
            .filter(rql)
        )
        return res.first()

    except ClientError as error:
        if error.status_code == 404:
            return
        handle_http_error(error)


def create_item(client, product_id, data):
    try:
        res = (
            client.products[product_id]
            .items
            .create(data)
        )
    except ClientError as error:
        handle_http_error(error)

    return res


def update_item(client, product_id, item_id, data):
    try:
        res = client.products[product_id].items[item_id].update(data)
    except ClientError as error:
        handle_http_error(error)

    return res


def delete_item(client, product_id, item_id):
    try:
        client.products[product_id].items[item_id].delete()
    except ClientError as error:
        handle_http_error(error)
