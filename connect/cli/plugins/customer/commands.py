# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.
import warnings

import click

from connect.cli.core import group
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.plugins.customer.export import dump_customers
from connect.cli.plugins.customer.sync import CustomerSynchronizer


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

    outfile = dump_customers(
        client=config.active.client,
        output_file=output_file,
        output_path=output_path,
        account_id=acc_id,
    )

    console.secho(
        f'\nCustomers of account {acc_id} have been successfully exported to {outfile}',
        fg='green',
    )


@grp_customer.command(
    name='sync',
    short_help='Synchronize customers from an excel file.',
)

@click.argument('input_file', metavar='input_file', nargs=1, required=True)  # noqa: E304
@pass_config
def cmd_sync_customers(config, input_file):
    acc_id = config.active.id

    if '.xlsx' not in input_file:
        input_file = f'{input_file}/{input_file}.xlsx'

    synchronizer = CustomerSynchronizer(
        client=config.active.client,
        account_id=acc_id,
    )
    warnings.filterwarnings("ignore", category=UserWarning)
    synchronizer.open(input_file, 'Customers')
    synchronizer.sync()
    synchronizer.save(input_file)
    synchronizer.stats.print()


def get_group():
    return grp_customer
