# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import warnings

import click

from connect.client import ConnectClient, RequestLogger
from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.plugins.customer.export import dump_customers
from connect.cli.plugins.customer.sync import CustomerSynchronizer
from connect.cli.plugins.customer.utils import print_sync_result


@group(name='customer', short_help='Export/synchronize customers.')
def grp_customer():
    pass  # pragma: no cover


@grp_customer.command(
    name='export',
    short_help='Export customers to an excel file.',
)
@click.option(
    '--output_path',
    '-p',
    'output_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory where to store the export.',
)
@click.option(
    '--out',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output Excel file name.',
)
@pass_config
def cmd_export_customers(config, output_path, output_file):
    acc_id = config.active.id
    acc_name = config.active.name
    if not config.silent:
        click.secho(
            f'Current active account: {acc_id} - {acc_name}\n',
            fg='blue',
        )
    outfile = dump_customers(
        api_url=config.active.endpoint,
        api_key=config.active.api_key,
        output_file=output_file,
        silent=config.silent,
        output_path=output_path,
        account_id=acc_id,
        verbose=config.verbose,
    )
    if not config.silent:
        click.secho(
            f'\nCustomers of account {acc_id} have been successfully exported to {outfile}',
            fg='green',
        )


@grp_customer.command(
    name='sync',
    short_help='Synchronize customers from an excel file.',
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
def cmd_sync_customers(config, input_file, yes):
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

    synchronizer = CustomerSynchronizer(
        client=client,
        silent=config.silent,
        account_id=acc_id,
    )
    warnings.filterwarnings("ignore", category=UserWarning)
    synchronizer.open(input_file, 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    synchronizer.save(input_file)
    if not config.silent:
        print_sync_result(skipped, created, updated, errors)


def get_group():
    return grp_customer
