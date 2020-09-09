# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect product-sync.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click

from cnctcli.actions.products import dump_products, sync_products
from cnctcli.config import pass_config


@click.group(name='product', short_help='commands related to product management')
def grp_product():
    pass


@grp_product.command(
    name='dump',
    short_help='dump products to an excel file',
)

@click.argument('product_ids', metavar='product_id', nargs=-1, required=True)  # noqa: E304
@click.option(
    '--out',
    '-o',
    'output_file',
    required=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Path to the output Excel file.'
)
@pass_config
def cmd_dump_products(config, product_ids, output_file):
    dump_products(config.api_url, config.api_key, product_ids, output_file)


@grp_product.command(
    name='sync',
    short_help='sync products from an excel file',
)

@click.option(  # noqa: E304
    '--in',
    '-i',
    'input_file',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help='Input Excel file for product synchronization.'
)
@pass_config
def cmd_sync_products(config, input_file):
    sync_products(config.api_url, config.api_key, input_file)
