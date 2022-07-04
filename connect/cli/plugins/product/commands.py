# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from functools import partial

import click
from click.exceptions import ClickException

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.shared.exceptions import SheetNotFoundError
from connect.cli.plugins.shared.translations_synchronizers import sync_product_translations
from connect.cli.plugins.product.clone import ProductCloner
from connect.cli.plugins.product.export import dump_product
from connect.cli.plugins.product.sync import (
    ActionsSynchronizer,
    CapabilitiesSynchronizer,
    ConfigurationValuesSynchronizer,
    GeneralSynchronizer,
    ItemSynchronizer,
    MediaSynchronizer,
    ParamsSynchronizer,
    StaticResourcesSynchronizer,
    TemplatesSynchronizer,
)
from connect.client import ClientError, R


@group(name='product', short_help='Manage product definitions.')
def grp_product():
    pass  # pragma: no cover


@grp_product.command(
    name='list',
    short_help='List products.',
)
@click.option(
    '--query',
    '-q',
    'query',
    help='RQL query expression.',
)
@pass_config
def cmd_list_products(config, query):
    if config.active.is_vendor():
        default_query = R().visibility.owner.eq(True) & R().version.null(True)
    else:
        default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)

    query = query or default_query
    query_products = config.active.client.products.filter(query).limit(console.page_size)

    console.table(
        columns=[
            'ID',
            'Name',
        ],
        rows=[
            (
                resource['id'],
                resource['name'],
            )
            for resource in query_products
        ],
    )


@grp_product.command(
    name='export',
    short_help='Export a product to an excel file.',
)

@click.argument('product_id', metavar='product_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--out',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output Excel file name.',
)
@click.option(
    '--output_path',
    '-p',
    'output_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory where to store the export.',
)
@pass_config
def cmd_dump_products(config, product_id, output_file, output_path):
    with console.progress() as progress:
        outfile = dump_product(
            config.active.client,
            product_id,
            output_file,
            progress,
            output_path,
        )

    console.secho(
        f'\nThe product {product_id} has been successfully exported to {outfile}.',
        fg='green',
    )


@grp_product.command(
    name='sync',
    short_help='Synchronize a product from an excel file.',
)
@click.argument('input_file', metavar='input_file', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_sync_products(config, input_file):
    if '.xlsx' not in input_file:
        input_file = f'{input_file}/{input_file}.xlsx'

    synchronizer = GeneralSynchronizer(config.active.client, None)
    product_id = synchronizer.open(input_file, 'General Information')

    console.confirm(
        'Are you sure you want to synchronize '
        f'the product {product_id} ?',
        abort=True,
    )
    console.echo('')

    with console.progress() as progress:
        general_errors = synchronizer.sync()
        if general_errors:
            errors = '\n'.join(general_errors)
            raise ClickException(
                f'Error synchronizing general product information: {errors}',
            )

        stats = SynchronizerStats(
            header=f'Results of synchronizing {product_id}',
        )

        sync_tasks = [
            item_sync,
            capabilities_sync,
            static_resources_sync,
            templates_sync,
            partial(params_sync, 'Ordering Parameters'),
            partial(params_sync, 'Fulfillment Parameters'),
            partial(params_sync, 'Configuration Parameters'),
            actions_sync,
            media_sync,
            config_values_sync,
        ]
        for task in sync_tasks:
            try:
                task(config.active.client, progress, input_file, stats)
            except SheetNotFoundError as e:
                console.secho(str(e), fg='blue')

        sync_product_translations(config.active.client, progress, input_file, stats)

    stats.print()


@grp_product.command(
    name='clone',
    short_help='Create a clone of a product.',
)

@click.argument('source_product_id', metavar='product_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--source_account',
    '-s',
    'source_account',
    help='Source account ID',
)
@click.option(
    '--destination_account',
    '-d',
    'destination_account',
    help='Destination account ID',
)
@click.option(
    '--new-product-name',
    '-n',
    'name',
    help='Cloned product name',
)
@pass_config
def cmd_clone_products(config, source_product_id, source_account, destination_account, name):
    if not config.active.is_vendor():
        raise ClickException(
            'The clone command is only available for vendor accounts.',
        )
    if name and len(name) > 32:
        raise ClickException(
            f'New product name can not exceed 32 chracters, provided as name {name}',
        )
    if destination_account:
        if not config.exists(destination_account):
            raise ClickException(f'The destination account {destination_account} does not exist.')
    else:
        destination_account = config.active.id

    if source_account:
        if not config.exists(source_account):
            raise ClickException(f'The source account {source_account} does not exist.')
    else:
        source_account = config.active.id

    console.confirm(
        'Are you sure you want to Clone '
        f'the product {source_product_id} ?',
        abort=True,
    )
    console.echo('')

    try:
        config.active.client.products[source_product_id].get()
    except ClientError:
        raise ClickException(f'Product {source_product_id} does not exist')

    stats = SynchronizerStats(
        operation='Clone',
        header=f'Results of cloning {source_product_id}',
    )

    with console.status_progress() as (status, progress):

        synchronizer = ProductCloner(
            config=config,
            source_account=source_account,
            destination_account=destination_account,
            product_id=source_product_id,
            progress=progress,
            stats=stats,
        )

        status.update(
            f'Dumping Product {synchronizer.product_id} from account '
            f'{synchronizer.source_account}',
            fg='blue',
        )

        synchronizer.dump()
        synchronizer.load_wb()

        status.update(
            f'Creating new Product on account {synchronizer.destination_account}',
            fg='blue',
        )

        synchronizer.create_product(name=name)
        synchronizer.clean_wb()

        status.update(
            'Injecting Product information',
            fg='blue',
        )

        synchronizer.inject()

        status.update(
            f'Finished cloning product {source_product_id} from account '
            f'{synchronizer.source_account} to {synchronizer.destination_account}\n',
            fg='green',
        )

        status.update('Done', fg='green')
    console.echo()
    console.secho(
        f'New product id {synchronizer.destination_product}',
        fg='green',
    )
    console.echo()
    stats.print()


def media_sync(client, progress, input_file, stats):
    synchronizer = MediaSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Media')
    synchronizer.sync()
    synchronizer.save(input_file)


def actions_sync(client, progress, input_file, stats):
    synchronizer = ActionsSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Actions')
    synchronizer.sync()
    synchronizer.save(input_file)


def templates_sync(client, progress, input_file, stats):
    synchronizer = TemplatesSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Templates')
    synchronizer.sync()
    synchronizer.save(input_file)


def params_sync(worksheet, client, progress, input_file, stats):
    synchronizer = ParamsSynchronizer(client, progress, stats)
    synchronizer.open(input_file, worksheet)
    synchronizer.sync()
    synchronizer.save(input_file)


def static_resources_sync(client, progress, input_file, stats):
    synchronizer = StaticResourcesSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Embedding Static Resources')
    synchronizer.sync()


def capabilities_sync(client, progress, input_file, stats):
    synchronizer = CapabilitiesSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Capabilities')
    synchronizer.sync()


def config_values_sync(client, progress, input_file, stats):
    synchronizer = ConfigurationValuesSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Configuration')
    synchronizer.sync()


def item_sync(client, progress, input_file, stats):
    synchronizer = ItemSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Items')
    synchronizer.sync()
    synchronizer.save(input_file)


def get_group():
    return grp_product
