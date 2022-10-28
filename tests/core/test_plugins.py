from importlib.metadata import EntryPoint

import click

from connect.cli.core.plugins import load_plugins


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
        return_value=iter([
            EntryPoint('internal', 'connect.cli.plugins.internal', None),
            EntryPoint('external', 'external.cli.plugin', None),
        ]),
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
        return_value=iter([
            EntryPoint('internal', 'connect.cli.plugins.internal', None),
        ]),
    )

    load_plugins(cli)

    assert 'internal' in cli.commands
    assert 'plugin' not in cli.commands
