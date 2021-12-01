import os

import click

from connect.cli import get_version
from connect.cli.core.account.commands import grp_account
from connect.cli.core.config import pass_config
from connect.cli.core.utils import check_for_updates


class CCliCommand(click.Command):
    def invoke(self, ctx):
        ctx.obj.validate()
        return super().invoke(ctx)


class CCliGroup(click.Group):
    def command(self, *args, **kwargs):
        from click.decorators import command
        kwargs['cls'] = CCliCommand

        def decorator(f):
            cmd = command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator


def group(name=None, **attrs):
    attrs.setdefault("cls", CCliGroup)
    return click.command(name, **attrs)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'CloudBlue Connect CLI, version {get_version()}')
    check_for_updates()
    ctx.exit()


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--version',
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=print_version,
)
@click.option('-c', '--config-dir',
              default=os.path.join(os.path.expanduser('~'), '.ccli'),
              type=click.Path(file_okay=False),
              help='set the config directory.')
@click.option(
    '-s',
    '--silent',
    is_flag=True,
    help='Prevent the output of informational messages.',
)
@click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Write verbose messages, including HTTP session',
)
@pass_config
@click.pass_context
def cli(ctx, config, config_dir, silent, verbose):
    """CloudBlue Connect Command Line Interface"""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config.load(config_dir)
    config.silent = silent
    config.verbose = verbose


cli.add_command(grp_account)
