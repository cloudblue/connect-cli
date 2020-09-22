# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click

from cnctcli.actions.products import dump_product, sync_product, validate_input_file
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
    acc_id = config.active.id
    acc_name = config.active.name
    click.echo(
        click.style(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    )
    outfile = dump_product(
        config.active.endpoint,
        config.active.api_key,
        product_id,
        output_file,
    )
    click.echo(
        click.style(
            f'\nThe product {product_id} has been successfully exported to {outfile}.',
            fg='green',
        )
    )


@grp_product.command(
    name='sync',
    short_help='sync a product from an excel file',
)

@click.argument('input_file', metavar='input_file', nargs=1, required=True)  # noqa: E304
@click.option(  # noqa: E304
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.'
)
@pass_config
def cmd_sync_products(config, input_file, yes):
    config.validate()
    acc_id = config.active.id
    acc_name = config.active.name
    click.echo(
        click.style(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    )
    product_id, wb = validate_input_file(
        config.active.endpoint,
        config.active.api_key,
        input_file,
    )

    if not yes:
        click.confirm(
            'Are you sure you want to synchronize '
            f'the items for the product {product_id} ?',
            abort=True,
        )
        click.echo('')
    sync_product(
        config.active.endpoint,
        config.active.api_key,
        product_id,
        wb,
    )

    wb.save(input_file)

    click.echo(
        click.style(
            f'\nThe product {product_id} has been successfully synchronized.',
            fg='green',
        )
    )
