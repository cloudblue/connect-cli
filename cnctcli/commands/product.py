# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

import click

from cnctcli.actions.products import (
    GeneralSynchronizer,
    ItemSynchronizer,
    CapabilitiesSynchronizer,
    StaticResourcesSynchronizer,
    TemplatesSynchronizer,
    ParamsSynchronizer,
    ActionsSynchronizer,
    dump_product,
)
from cnctcli.commands.utils import continue_or_quit
from cnctcli.config import pass_config
from cnct import ConnectClient
from cnct.rql import R
from cnctcli.actions.products.utils import SheetNotFoundError


@click.group(name='product', short_help='commands related to product management')
def grp_product():
    pass  # pragma: no cover


@grp_product.command(
    name='list',
    short_help='list products',
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
            )
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
    )

    if acc_id.startswith('VA'):
        default_query = R().visibility.owner.eq(True) & R().version.null(True)
    else:
        default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)

    query = query or default_query
    paging = 0
    query_products = client.products.filter(query).limit(page_size)

    for prod in query_products:
        paging += 1
        click.echo(
            f"{prod['id']} - {prod['name']}"
        )
        if paging % page_size == 0 and paging != query_products.count() and not always_continue:
            if not continue_or_quit():
                return


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
    if not config.silent:
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
        config.silent,
    )
    if not config.silent:
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
    if not config.silent:
        click.echo(
            click.style(
                f'Current active account: {acc_id} - {acc_name}\n',
                fg='blue',
            )
        )
    client = ConnectClient(
        api_key=config.active.api_key,
        endpoint=config.active.endpoint,
        validate_using_specs=False,
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
    # Sync Items first
    try:
        print_next_task('Items', product_id, config.silent)
        item_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Items', product_id, config.silent)
    try:
        print_next_task('Capabilities', product_id, config.silent)
        capabilities_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Capabilities', product_id, config.silent)

    try:
        print_next_task('Embedding resources', product_id, config.silent)
        static_resources_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Embedding resources', product_id, config.silent)

    try:
        print_next_task('Templates', product_id, config.silent)
        templates_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Embedding resources', product_id, config.silent)

    param_task(client, config, input_file, product_id, 'Ordering Parameters')
    param_task(client, config, input_file, product_id, 'Fulfillment Parameters')
    param_task(client, config, input_file, product_id, 'Configuration Parameters')

    print_finished_task('Actions', product_id, config.silent)

    try:
        print_next_task('Actions', product_id, config.silent)
        actions_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Actions', product_id, config.silent)


def param_task(client, config, input_file, product_id, param_type):
    try:
        print_next_task(param_type, product_id, config.silent)
        params_sync(client, config, input_file, param_type)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task(param_type, product_id, config.silent)


def actions_sync(client, config, input_file):
    synchronizer = ActionsSynchronizer(
        client,
        config.silent,
    )

    product_id = synchronizer.open(input_file, 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)
    print_action_result(
        silent=config.silent,
        obj_type='Actions',
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def templates_sync(client, config, input_file):
    synchronizer = TemplatesSynchronizer(
        client,
        config.silent,
    )

    product_id = synchronizer.open(input_file, 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)
    print_action_result(
        silent=config.silent,
        obj_type='Templates',
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def params_sync(client, config, input_file, param_type):
    synchronizer = ParamsSynchronizer(
        client,
        config.silent,
    )

    product_id = synchronizer.open(input_file, param_type)

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)

    print_action_result(
        silent=config.silent,
        obj_type=param_type,
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def static_resources_sync(client, config, input_file):
    synchronizer = StaticResourcesSynchronizer(
        client,
        config.silent,
    )
    product_id = synchronizer.open(input_file, 'Embedding Static Resources')

    skipped, created, deleted, errors = synchronizer.sync()

    print_action_result(
        silent=config.silent,
        obj_type='Embedding resources',
        product_id=product_id,
        created=created,
        updated=0,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def capabilities_sync(client, config, input_file):

    synchronizer = CapabilitiesSynchronizer(
        client,
        config.silent,
    )
    product_id = synchronizer.open(input_file, 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    print_action_result(
        silent=config.silent,
        obj_type='Capabilities',
        product_id=product_id,
        created=0,
        updated=updated,
        deleted=0,
        skipped=skipped,
        errors=errors,
    )


def item_sync(client, config, input_file):

    synchronizer = ItemSynchronizer(
        client,
        config.silent,
    )
    product_id = synchronizer.open(input_file, 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)
    print_action_result(
        silent=config.silent,
        obj_type='Items',
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def print_next_task(task, product, silent):
    if not silent:
        click.echo(f'Going to synchronize tab from Excel workbook {task} for product {product}\n')


def print_finished_task(task, product, silent):
    if not silent:
        click.echo(
            f'Finished synchronization of tab from Excel workbook {task} for product {product}\n'
        )


def print_action_result(
        silent,
        obj_type,
        product_id,
        created,
        updated,
        deleted,
        skipped,
        errors,
):
    if not silent:
        msg = f'\nThe {obj_type} of product {product_id} has been synchronized.'
        fg = 'green'

        if errors:
            msg = f'\nThe {obj_type} of product {product_id} has been partially synchronized.'
            fg = 'yellow'

        errors_count = len(errors)
        processed = skipped + updated + errors_count

        click.echo(click.style(msg, fg=fg))

        click.echo(
            click.style(
                (
                    f'\nProcessed rows: {processed}\n'
                    f'  - Created: {created}\n'
                    f'  - Updated: {updated}\n'
                    f'  - Deleted: {deleted}\n'
                    f'  - Skipped: {skipped}\n'
                    f'  - Errors: {errors_count}\n'
                ),
                fg='blue'
            )
        )

        if errors:
            click.echo(
                click.style('\nErrors:\n', fg='magenta')
            )
            for row_idx, messages in errors.items():
                click.echo(f'  Errors at row #{row_idx}')
                for msg in messages:
                    click.echo(f'    - {msg}')
                click.echo(' ')
