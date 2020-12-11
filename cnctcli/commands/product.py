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
    ConfigurationValuesSynchronizer,
    MediaSynchronizer,
    dump_product,
    ProductCloner,
)
from cnctcli.commands.utils import continue_or_quit
from cnctcli.config import pass_config
from cnct import ConnectClient, ClientError
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
        use_specs=False,
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
    help='Output Excel file name.'
)
@click.option(
    '--output_path',
    '-p',
    'output_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory where to store the export'
)
@pass_config
def cmd_dump_products(config, product_id, output_file, output_path):
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
        output_path,
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

    if '.xlsx' not in input_file:
        input_file = f'{input_file}/{input_file}.xlsx'

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
        use_specs=False,
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

    print_next_task('General Information', product_id, config.silent)
    general_errors = synchronizer.sync()
    if general_errors and not config.silent:
        click.echo(
            click.style(
                f'\nError synchronizing general product information: {".".join(general_errors)}\n',
                fg='magenta'
            )
        )
    print_finished_task('General Information', product_id, config.silent)

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

    try:
        print_next_task('Media', product_id, config.silent)
        media_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Media', product_id, config.silent)

    try:
        print_next_task('Configuration', product_id, config.silent)
        config_values_sync(client, config, input_file)
    except SheetNotFoundError as e:
        if not config.silent:
            click.echo(
                click.style(
                    str(e),
                    fg='blue',
                )
            )
    print_finished_task('Configuration', product_id, config.silent)


@grp_product.command(
    name='clone',
    short_help='Clone a product',
)

@click.argument('source_product_id', metavar='product_id', nargs=1, required=True)  # noqa: E304
@click.option(
    '--source_account',
    '-s',
    'source_account',
    help='Source account ID'
)
@click.option(
    '--destination_account',
    '-d',
    'destination_account',
    help='Destination account ID'
)
@click.option(
    '--new-product-name',
    '-n',
    'name',
    help='Cloned product name'
)
@click.option(  # noqa: E304
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.'
)
@pass_config
def cmd_clone_products(config, source_product_id, source_account, destination_account, name, yes):
    if name and len(name) > 32:
        click.echo(
            click.style(
                f'New product name can not exceed 32 chracters, provided as name{name}',
                fg='red',
            )
        )
        exit(-1)
    if destination_account:
        config.activate(destination_account)
        config.validate()
    else:
        destination_account = config.active.id

    if source_account:
        config.activate(source_account)
        config.validate()
    else:
        source_account = config.active.id

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
        use_specs=False,
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
            )
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
            )
        )

    synchronizer.dump()
    synchronizer.load_wb()

    if not config.silent:
        click.echo(
            click.style(
                f'Creating new Product on account {synchronizer.destination_account}',
                fg='blue',
            )
        )

    synchronizer.create_product(name=name)
    synchronizer.clean_wb()

    if not config.silent:
        click.echo(
            click.style(
                'Injecting Product information',
                fg='blue',
            )
        )

    synchronizer.inject()

    if not config.silent:
        click.echo(
            click.style(
                f'Finished cloning product {source_product_id} from account '
                f'{synchronizer.source_account} to {synchronizer.destination_account}\n',
                fg='green'
            )
        )

        click.echo(
            click.style(
                f'New product id {synchronizer.destination_product}',
                fg='green'
            )
        )


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


def media_sync(client, config, input_file):
    synchronizer = MediaSynchronizer(
        client,
        config.silent,
    )

    product_id = synchronizer.open(input_file, 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    synchronizer.save(input_file)

    print_action_result(
        silent=config.silent,
        obj_type='Media',
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
        skipped=skipped,
        errors=errors,
    )


def actions_sync(client, config, input_file):
    synchronizer = ActionsSynchronizer(
        client,
        config.silent,
    )

    product_id = synchronizer.open(input_file, 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

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


def config_values_sync(client, config, input_file):
    synchronizer = ConfigurationValuesSynchronizer(
        client,
        config.silent,
    )
    product_id = synchronizer.open(input_file, 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    print_action_result(
        silent=config.silent,
        obj_type='Configuration',
        product_id=product_id,
        created=created,
        updated=updated,
        deleted=deleted,
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
