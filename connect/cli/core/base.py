import os

import click

from connect.cli import get_version
from connect.cli.core.account.commands import grp_account
from connect.cli.core.config import pass_config
from connect.cli.core.terminal import console
from connect.cli.core.utils import check_for_updates


class CCliCommand(click.Command):
    def invoke(self, ctx):
        ctx.obj.validate()
        active_account = ctx.obj.active
        console.secho(
            f'Current active account: {active_account.id} - {active_account.name}\n',
            fg='blue',
        )
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

    def group(self, *args, **kwargs):
        from click.decorators import group

        kwargs['cls'] = CCliGroup

        def decorator(f):
            cmd = group(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator


class LazyGroup(click.Group):
    """A group that imports a subgroup only when it is called.

    Until then, `ccli --help` lists the subgroup by the short help it was added with.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lazy_commands = {}

    def add_lazy_command(self, name, short_help, entrypoint):
        if name not in self.commands:
            self.lazy_commands[name] = (short_help, entrypoint)

    def list_commands(self, ctx):
        return sorted({*super().list_commands(ctx), *self.lazy_commands})

    def get_command(self, ctx, cmd_name):
        if cmd_name in self.lazy_commands:
            _, entrypoint = self.lazy_commands[cmd_name]
            self.add_command(entrypoint.load()(), cmd_name)
            del self.lazy_commands[cmd_name]
        return super().get_command(ctx, cmd_name)

    def format_commands(self, ctx, formatter):
        commands = []
        for name in self.list_commands(ctx):
            if name in self.lazy_commands:
                commands.append((name, self.lazy_commands[name][0]))
                continue
            cmd = super().get_command(ctx, name)
            if cmd is not None and not cmd.hidden:
                commands.append((name, cmd))
        if commands:
            limit = formatter.width - 6 - max(len(name) for name, _ in commands)
            with formatter.section('Commands'):
                formatter.write_dl(
                    [
                        (name, cmd if isinstance(cmd, str) else cmd.get_short_help_str(limit))
                        for name, cmd in commands
                    ],
                )


def group(name=None, **attrs):
    attrs.setdefault('cls', CCliGroup)
    return click.command(name, **attrs)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    console.echo(f'CloudBlue Connect CLI, version {get_version()}')
    check_for_updates()
    ctx.exit()


@click.group(cls=LazyGroup, context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--version',
    is_flag=True,
    expose_value=False,
    is_eager=True,
    callback=print_version,
)
@click.option(
    '-c',
    '--config-dir',
    default=os.path.join(os.path.expanduser('~'), '.ccli'),
    type=click.Path(file_okay=False),
    help='set the config directory.',
)
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
@click.option(  # noqa: E304
    '--yes',
    '-y',
    'yes',
    is_flag=True,
    help='Answer yes to all questions.',
)
@click.option(
    '--page-size',
    '-p',
    'page_size',
    type=click.IntRange(1),
    help='Number of items per page.',
    default=25,
)
@pass_config
@click.pass_context
def cli(ctx, config, config_dir, silent, verbose, yes, page_size):
    """CloudBlue Connect Command Line Interface"""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config.load(config_dir)

    console.silent = silent
    console.verbose = verbose
    console.skip_confirm = yes
    console.page_size = page_size


cli.add_command(grp_account)
