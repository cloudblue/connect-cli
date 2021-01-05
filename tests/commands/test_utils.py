from unittest.mock import patch
from cnctcli.commands import utils


def test_continue_or_quit_c():
    with patch(
        'cnctcli.commands.utils.click.echo'
    ):
        with patch(
            'cnctcli.commands.utils.click.getchar',
            return_value='c'
        ):
            assert utils.continue_or_quit() is True


def test_continue_or_quit_q():
    with patch(
        'cnctcli.commands.utils.click.echo'
    ):
        with patch(
            'cnctcli.commands.utils.click.getchar',
            return_value='q'
        ):
            assert utils.continue_or_quit() is False
