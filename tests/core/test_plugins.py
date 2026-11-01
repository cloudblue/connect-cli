import subprocess
import sys
from importlib.metadata import EntryPoint

import click

from connect.cli.core.base import LazyGroup
from connect.cli.core.plugins import BUILTIN_GROUPS, load_plugins
from connect.cli.core.utils import iter_entry_points


def test_load_plugins(mocker):
    cli = click.Group()

    grp_internal = click.MultiCommand('internal')
    grp_external = click.MultiCommand('external')

    mocker.patch.object(
        EntryPoint,
        'load',
        side_effect=[
            lambda: grp_internal,
            lambda: grp_external,
        ],
    )
    mocker.patch(
        'connect.cli.core.plugins.iter_entry_points',
        return_value=iter(
            [
                EntryPoint('internal', 'connect.cli.plugins.internal', None),
                EntryPoint('external', 'external.cli.plugin', None),
            ],
        ),
    )

    load_plugins(cli)

    assert 'internal' in cli.commands
    assert 'plugin' in cli.commands
    assert 'external' in cli.commands['plugin'].commands


def test_load_no_external(mocker):
    cli = click.Group()
    grp_internal = click.MultiCommand('internal')

    mocker.patch.object(
        EntryPoint,
        'load',
        side_effect=[
            lambda: grp_internal,
        ],
    )
    mocker.patch(
        'connect.cli.core.plugins.iter_entry_points',
        return_value=iter(
            [
                EntryPoint('internal', 'connect.cli.plugins.internal', None),
            ],
        ),
    )

    load_plugins(cli)

    assert 'internal' in cli.commands
    assert 'plugin' not in cli.commands


def test_builtin_groups_match_the_installed_plugins():
    entrypoints = {
        ep.name: ep
        for ep in iter_entry_points('connect.cli.plugins')
        if ep.value.startswith('connect.cli.plugins.')
    }

    assert set(entrypoints) == set(BUILTIN_GROUPS)
    for ep_name, (name, short_help) in BUILTIN_GROUPS.items():
        grp = entrypoints[ep_name].load()()
        assert (grp.name, grp.short_help) == (name, short_help)


def test_load_plugins_adds_builtin_groups_lazily(mocker):
    cli = LazyGroup()
    cli.add_command(click.Command('account', short_help='Manage accounts.'))
    cli.add_command(click.Command('secret', hidden=True))
    grp_product = click.Group('product', short_help='Manage product definitions.')
    load = mocker.patch.object(EntryPoint, 'load', return_value=lambda: grp_product)
    mocker.patch(
        'connect.cli.core.plugins.iter_entry_points',
        return_value=iter(
            [
                EntryPoint('product', 'connect.cli.plugins.product.commands:get_group', None),
            ],
        ),
    )

    load_plugins(cli)
    ctx = click.Context(cli)
    help_text = cli.get_help(ctx)

    assert 'product' not in cli.commands
    assert cli.list_commands(ctx) == ['account', 'product', 'secret']
    assert 'Manage accounts.' in help_text
    assert 'Manage product definitions.' in help_text
    assert 'secret' not in help_text
    load.assert_not_called()

    assert cli.get_command(ctx, 'product') is grp_product
    assert cli.get_command(ctx, 'product') is grp_product
    load.assert_called_once()
    assert cli.lazy_commands == {}

    cli.add_lazy_command('product', 'Manage product definitions.', None)
    assert cli.lazy_commands == {}


def test_lazy_group_without_commands_has_no_commands_section():
    cli = LazyGroup()

    assert 'Commands' not in cli.get_help(click.Context(cli))


def test_help_imports_no_command_group():
    code = (
        'import sys\n'
        "sys.argv = ['ccli', '--help']\n"
        'from connect.cli.ccli import main\n'
        'main()\n'
        "print(sorted(m for m in sys.modules if m.startswith('connect.cli.plugins.')), file=sys.stderr)\n"
    )

    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True, check=True
    )

    assert 'Manage product definitions.' in result.stdout
    assert result.stderr.strip().splitlines()[-1] == '[]'
