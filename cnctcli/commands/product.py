# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click

from cnctcli.actions.products import dump_product, sync_product
from cnctcli.config import pass_config


@click.group(name='product', short_help='commands related to product management')
def grp_product():
    pass  # pragma: no cover


@grp_product.command(
    name='export',
    short_help='export a product to an excel file',
)

@click.argument('product_id', metavar='product_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--out',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Path to the output Excel file.'
)
@pass_config
def cmd_dump_products(config, product_id, output_file):
    config.validate()
    outfile = dump_product(
        config.active.endpoint,
        config.active.api_key,
        product_id,
        output_file,
    )
    click.echo(
        click.style(
            f'Product {product_id} exported successfully to {outfile}',
            fg='green',
        )
    )


@grp_product.command(
    name='sync',
    short_help='sync a product from an excel file',
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
    sync_product(config.active.endpoint, config.active.api_key, input_file)
