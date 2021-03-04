# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import click
import warnings
from cnctcli.config import pass_config
from cnctcli.actions import customers
from cnct import ConnectClient
from cnctcli.actions.customers_syncronizer import CustomerSynchronizer
from cmr import render
from cnctcli.commands.utils import continue_or_quit


@click.group(name='customer', short_help='commands related to customer management')
def grp_customer():
    pass  # pragma: no cover


@grp_customer.command(
    name='export',
    short_help='export customers',
)
@click.option(
    '--output_path',
    '-p',
    'output_path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory where to store the export'
)
@click.option(
    '--out',
    '-o',
    'output_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    help='Output Excel file name.'
)
@pass_config
def cmd_export_customers(config, output_path, output_file):
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
    outfile = customers.dump_customers(
        api_url=config.active.endpoint,
        api_key=config.active.api_key,
        output_file=output_file,
        silent=config.silent,
        output_path=output_path,
        account_id=acc_id,
    )
    if not config.silent:
        click.echo(
            click.style(
                f'\nCustomers of account {acc_id} has been successfully exported to {outfile}',
                fg='green',
            )
        )


@grp_customer.command(
    name='sync',
    short_help='sync customers from an excel file',
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
def cmd_sync_customers(config, input_file, yes):
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
        max_retries=3,
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
        msg = '''
# Results of synchronization


| Module | Processed | Created | Updated | Deleted | Skipped | Errors |
|:--------|--------:| --------:|--------:|----------:|----------:|----------:|
'''
        errors_count = len(errors)
        processed = skipped + created + updated + errors_count
        row = '|{module}|{processed}|{created}|{updated}|{deleted}|{skipped}|{errors}|\n'
        msg += row.format(
            module='Customers Synchronizer',
            processed=processed,
            created=created,
            updated=updated,
            deleted=0,
            skipped=skipped,
            errors=errors_count
        )
        click.echo(
            f'\n{render(msg)}\n'
        )
        if len(errors) > 0:
            msg = f'\nSync operation had {len(errors)} errors, do you want to see them?'
            fg = 'yellow'

            click.echo(click.style(msg, fg=fg))

            print_errors = continue_or_quit()

            if print_errors:
                for row_idx, messages in errors.items():
                    click.echo(f'  Errors at row #{row_idx}')
                    for msg in messages:
                        click.echo(f'    - {msg}')
                    click.echo(' ')
