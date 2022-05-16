# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import click
from click.exceptions import ClickException

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.utils import continue_or_quit
from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.shared.exceptions import SheetNotFoundError
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
from connect.client import ClientError, ConnectClient, R, RequestLogger


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
@click.option(
    '--page-size',
    '-p',
    'page_size',
    type=int,
    help='Number of products per page.',
    default=25,
)
@click.option(
    '--always-continue',
    '-c',
    'always_continue',
    is_flag=True,
    help='Do not prompt to continue.',
)
@pass_config
def cmd_list_products(config, query, page_size, always_continue):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )

    if config.active.is_vendor():
        default_query = R().visibility.owner.eq(True) & R().version.null(True)
    else:
        default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)

    query = query or default_query
    paging = 0
    query_products = client.products.filter(query).limit(page_size)

    for prod in query_products:
        paging += 1
        click.echo(
            f"{prod['id']} - {prod['name']}",
        )
        if paging % page_size == 0 and paging != query_products.count() and not always_continue:
            if not continue_or_quit():
                return


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
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    outfile = dump_product(
        config.active.endpoint,
        config.active.api_key,
        product_id,
        output_file,
        config.silent,
        config.verbose,
        output_path,
    )
    if not config.silent:
        click.secho(
            f'\nThe product {product_id} has been successfully exported to {outfile}.',
            fg='green',
        )


@grp_product.command(
    name='sync',
    short_help='Synchronize a product from an excel file.',
)
@click.argument('input_file', metavar='input_file', nargs=1, required=True)  # noqa: E304
@click.option(  # noqa: E304
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.',
)
@pass_config
def cmd_sync_products(config, input_file, yes):  # noqa: CCR001
    acc_id = config.active.id
    acc_name = config.active.name

    if '.xlsx' not in input_file:
        input_file = f'{input_file}/{input_file}.xlsx'

    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )

    synchronizer = GeneralSynchronizer(client, config.silent)
    product_id = synchronizer.open(input_file, 'General Information')

    if not yes:
        click.confirm(
            'Are you sure you want to synchronize '
            f'the product {product_id} ?',
            abort=True,
        )
        click.echo('')

    general_errors = synchronizer.sync()
    if general_errors and not config.silent:
        click.secho(
            f'\nError synchronizing general product information: {".".join(general_errors)}\n',
            fg='magenta',
        )
    stats = SynchronizerStats()
    stats.RESULTS_HEADER = stats.RESULTS_HEADER.replace(
        "synchronization", f"synchronizing {product_id}",
    )

    try:
        item_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')
    try:
        capabilities_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

    try:
        static_resources_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

    try:
        templates_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

    param_task(client, config, input_file, 'Ordering Parameters', stats)
    param_task(client, config, input_file, 'Fulfillment Parameters', stats)
    param_task(client, config, input_file, 'Configuration Parameters', stats)

    try:
        actions_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

    try:
        media_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

    try:
        config_values_sync(client, config, input_file, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')

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
@click.option(  # noqa: E304
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.',
)
@pass_config
def cmd_clone_products(config, source_product_id, source_account, destination_account, name, yes):
    if not config.active.is_vendor():
        raise ClickException(
            'The clone command is only available for vendor accounts.',
        )
    if name and len(name) > 32:
        click.secho(
            f'New product name can not exceed 32 chracters, provided as name {name}',
            fg='red',
        )
        exit(-1)
    if destination_account:
        config.activate(destination_account)
    else:
        destination_account = config.active.id

    if source_account:
        config.activate(source_account)
    else:
        source_account = config.active.id

    acc_id = config.active.id
    acc_name = config.active.name

    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )

    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )

    if not yes:
        click.confirm(
            'Are you sure you want to Clone '
            f'the product {source_product_id} ?',
            abort=True,
        )
        click.echo('')

    try:
        client.products[source_product_id].get()
    except ClientError:
        click.secho(
            f'Product {source_product_id} does not exist',
            fg='red',
        )
        exit(-1)

    synchronizer = ProductCloner(
        config=config,
        source_account=source_account,
        destination_account=destination_account,
        product_id=source_product_id,

    )

    if not config.silent:
        click.secho(
            f'Dumping Product {synchronizer.product_id} from account '
            f'{synchronizer.source_account}\n',
            fg='blue',
        )

    synchronizer.dump()
    synchronizer.load_wb()

    if not config.silent:
        click.secho(
            f'Creating new Product on account {synchronizer.destination_account}',
            fg='blue',
        )

    synchronizer.create_product(name=name)
    synchronizer.clean_wb()

    if not config.silent:
        click.secho(
            'Injecting Product information',
            fg='blue',
        )

    synchronizer.inject()

    if not config.silent:
        click.secho(
            f'Finished cloning product {source_product_id} from account '
            f'{synchronizer.source_account} to {synchronizer.destination_account}\n',
            fg='green',
        )

        click.secho(
            f'New product id {synchronizer.destination_product}',
            fg='green',
        )


def param_task(client, config, input_file, worksheet, stats):
    try:
        result = params_sync(client, config, input_file, worksheet, stats)
    except SheetNotFoundError as e:
        if not config.silent:
            click.secho(str(e), fg='blue')
    return result


def media_sync(client, config, input_file, stats):
    synchronizer = MediaSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Media')
    synchronizer.sync()
    synchronizer.save(input_file)


def actions_sync(client, config, input_file, stats):
    synchronizer = ActionsSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Actions')
    synchronizer.sync()


def templates_sync(client, config, input_file, stats):
    synchronizer = TemplatesSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Templates')
    synchronizer.sync()
    synchronizer.save(input_file)


def params_sync(client, config, input_file, worksheet, stats):
    synchronizer = ParamsSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, worksheet)
    synchronizer.sync()
    synchronizer.save(input_file)


def static_resources_sync(client, config, input_file, stats):
    synchronizer = StaticResourcesSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Embedding Static Resources')
    synchronizer.sync()


def capabilities_sync(client, config, input_file, stats):
    synchronizer = CapabilitiesSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Capabilities')
    synchronizer.sync()


def config_values_sync(client, config, input_file, stats):
    synchronizer = ConfigurationValuesSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Configuration')
    synchronizer.sync()


def item_sync(client, config, input_file, stats):
    synchronizer = ItemSynchronizer(client, config.silent, stats)
    synchronizer.open(input_file, 'Items')
    synchronizer.sync()
    synchronizer.save(input_file)


def get_group():
    return grp_product
