import click
import pkg_resources


def load_plugins(cli):
    @click.group(name='plugin', short_help='Third party plugins.')
    def grp_plugins():
        pass  # pragma: no cover

    has_3rd_party_plugins = False

    for entrypoint in pkg_resources.iter_entry_points('connect.cli.plugins'):
        if entrypoint.module_name.startswith('connect.cli.plugins.'):
            command_fn = entrypoint.load()
            cli.add_command(command_fn())
        else:
            has_3rd_party_plugins = True
            command_fn = entrypoint.load()
            grp_plugins.add_command(command_fn())

    if has_3rd_party_plugins:
        cli.add_command(grp_plugins)
