# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import click
from click.exceptions import ClickException
from cmr import render

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.utils import continue_or_quit
from connect.cli.plugins.exceptions import SheetNotFoundError
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
        click.echo(
            click.style(
                f'Current active account: {acc_id} - {acc_name}\n',
                fg='blue',
            ),
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
        click.echo(
            click.style(
                f'Current active account: {acc_id} - {acc_name}\n',
                fg='blue',
            ),
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
        click.echo(
            click.style(
                f'\nThe product {product_id} has been successfully exported to {outfile}.',
                fg='green',
            ),
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
        click.echo(
            click.style(
                f'Current active account: {acc_id} - {acc_name}\n',
                fg='blue',
            ),
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
        max_retries=3,
        logger=RequestLogger() if config.verbose else None,
    )

    synchronizer = GeneralSynchronizer(
        client,
        config.silent,
    )
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
        click.echo(
            click.style(
                f'\nError synchronizing general product information: {".".join(general_errors)}\n',
                fg='magenta',
            ),
        )
    results_tracker = []

    try:
        results_tracker.append(item_sync(client, config, input_file))
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )
    try:
        results_tracker.append(capabilities_sync(client, config, input_file))
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    try:
        results_tracker.append(static_resources_sync(client, config, input_file))
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    try:
        results_tracker.append(templates_sync(client, config, input_file))
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    results_tracker.append(
        param_task(
            client,
            config,
            input_file,
            product_id,
            'Ordering Parameters',
        ),
    )
    results_tracker.append(
        param_task(
            client,
            config,
            input_file,
            product_id,
            'Fulfillment Parameters',
        ),
    )
    results_tracker.append(
        param_task(
            client,
            config,
            input_file,
            product_id,
            'Configuration Parameters',
        ),
    )

    try:
        results_tracker.append(
            actions_sync(
                client,
                config,
                input_file,
            ),
        )
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    try:
        results_tracker.append(
            media_sync(
                client,
                config,
                input_file,
            ),
        )
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    try:
        results_tracker.append(
            config_values_sync(
                client,
                config,
                input_file,
            ),
        )
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )

    print_results(
        product_id=product_id,
        silent=config.silent,
        results_tracker=results_tracker,
    )


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
        click.echo(
            click.style(
                f'New product name can not exceed 32 chracters, provided as name {name}',
                fg='red',
            ),
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
        click.echo(
            click.style(
                f'Current active account: {acc_id} - {acc_name}\n',
                fg='blue',
            ),
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
        click.echo(
            click.style(
                f'Product {source_product_id} does not exist',
                fg='red',
            ),
        )
        exit(-1)

    synchronizer = ProductCloner(
        config=config,
        source_account=source_account,
        destination_account=destination_account,
        product_id=source_product_id,

    )

    if not config.silent:
        click.echo(
            click.style(
                f'Dumping Product {synchronizer.product_id} from account '
                f'{synchronizer.source_account}\n',
                fg='blue',
            ),
        )

    synchronizer.dump()
    synchronizer.load_wb()

    if not config.silent:
        click.echo(
            click.style(
                f'Creating new Product on account {synchronizer.destination_account}',
                fg='blue',
            ),
        )

    synchronizer.create_product(name=name)
    synchronizer.clean_wb()

    if not config.silent:
        click.echo(
            click.style(
                'Injecting Product information',
                fg='blue',
            ),
        )

    synchronizer.inject()

    if not config.silent:
        click.echo(
            click.style(
                f'Finished cloning product {source_product_id} from account '
                f'{synchronizer.source_account} to {synchronizer.destination_account}\n',
                fg='green',
            ),
        )

        click.echo(
            click.style(
                f'New product id {synchronizer.destination_product}',
                fg='green',
            ),
        )


def param_task(client, config, input_file, product_id, param_type):
    try:
        result = params_sync(client, config, input_file, param_type)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                ),
            )
    return result


def media_sync(client, config, input_file):
    synchronizer = MediaSynchronizer(
        client,
        config.silent,
    )

    synchronizer.open(input_file, 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)

    return {
        "module": "Media",
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def actions_sync(client, config, input_file):
    synchronizer = ActionsSynchronizer(
        client,
        config.silent,
    )

    synchronizer.open(input_file, 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    return {
        "module": "Actions",
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def templates_sync(client, config, input_file):
    synchronizer = TemplatesSynchronizer(
        client,
        config.silent,
    )

    synchronizer.open(input_file, 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)
    return {
        "module": "Templates",
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def params_sync(client, config, input_file, param_type):
    synchronizer = ParamsSynchronizer(
        client,
        config.silent,
    )

    synchronizer.open(input_file, param_type)

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)

    return {
        "module": param_type,
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def static_resources_sync(client, config, input_file):
    synchronizer = StaticResourcesSynchronizer(
        client,
        config.silent,
    )
    synchronizer.open(input_file, 'Embedding Static Resources')

    skipped, created, deleted, errors = synchronizer.sync()

    return {
        "module": "Static Resources",
        "created": created,
        "updated": 0,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def capabilities_sync(client, config, input_file):

    synchronizer = CapabilitiesSynchronizer(
        client,
        config.silent,
    )
    synchronizer.open(input_file, 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    return {
        "module": "Capabilities",
        "created": 0,
        "updated": updated,
        "deleted": 0,
        "skipped": skipped,
        "errors": errors,
    }


def config_values_sync(client, config, input_file):
    synchronizer = ConfigurationValuesSynchronizer(
        client,
        config.silent,
    )
    synchronizer.open(input_file, 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    return {
        "module": "Configuration",
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def item_sync(client, config, input_file):
    synchronizer = ItemSynchronizer(
        client,
        config.silent,
    )
    synchronizer.open(input_file, 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)
    return {
        "module": "Items",
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
    }


def print_results(  # noqa: CCR001
        silent,
        product_id,
        results_tracker,
):
    if not silent:
        msg = f'''
# Results of synchronizing {product_id}


| Module | Processed | Created | Updated | Deleted | Skipped | Errors |
|:--------|--------:| --------:|--------:|----------:|----------:|----------:|
        '''
        errors = 0
        for result in results_tracker:
            errors_count = len(result['errors'])
            errors += errors_count
            processed = result['skipped'] + result['created']
            processed += result['updated'] + result['deleted']
            processed += errors_count
            row = '|{module}|{processed}|{created}|{updated}|{deleted}|{skipped}|{errors}|\n'
            msg += row.format(
                module=result['module'],
                processed=processed,
                created=result['created'],
                updated=result['updated'],
                deleted=result['deleted'],
                skipped=result['skipped'],
                errors=errors_count,
            )
        click.echo(
            f'\n{render(msg)}\n',
        )

        if errors > 0:
            msg = f'\nSync operation had {errors} errors, do you want to see them?'
            fg = 'yellow'

            click.echo(click.style(msg, fg=fg))

            print_errors = continue_or_quit()

            if print_errors:
                for result in results_tracker:
                    if len(result['errors']) > 0:
                        click.echo(
                            click.style(f'\nModule {result["module"]}:\n', fg='magenta'),
                        )
                        for row_idx, messages in result["errors"].items():
                            click.echo(f'  Errors at row #{row_idx}')
                            for msg in messages:
                                click.echo(f'    - {msg}')
                            click.echo(' ')


def get_group():
    return grp_product
