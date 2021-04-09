import click
from cmr import render

from connect.cli.core.utils import continue_or_quit
from connect.cli.plugins.customer.constants import SYNC_RESULT_OUTPUT


def print_sync_result(skipped, created, updated, errors):
    msg = SYNC_RESULT_OUTPUT

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
        errors=errors_count,
    )
    click.echo(
        f'\n{render(msg)}\n',
    )
    if len(errors) > 0:
        msg = f'\nSync operation had {len(errors)} errors, do you want to see them?'
        fg = 'yellow'

        click.secho(msg, fg=fg)

        print_errors = continue_or_quit()

        if print_errors:
            for row_idx, messages in errors.items():
                click.echo(f'  Errors at row #{row_idx}')
                for msg in messages:
                    click.echo(f'    - {msg}')
                click.echo(' ')
