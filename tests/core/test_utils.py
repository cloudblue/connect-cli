import json
import subprocess

from connect.cli.core import utils


def test_continue_or_quit_c(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', return_value='c')
    assert utils.continue_or_quit() is True


def test_continue_or_quit_q(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', return_value='q')
    assert utils.continue_or_quit() is False


def test_continue_or_quit_invalid_plus_q(mocker):
    mocker.patch('connect.cli.core.utils.click.echo')
    mocker.patch('connect.cli.core.utils.click.getchar', side_effect=['z', 'q'])
    assert utils.continue_or_quit() is False


def test_check_for_updates_ok(mocker, capsys):
    pip_resp = [
        {
            'name': 'connect-cli',
            'version': '1.0.0',
            'latest_version': '2.0.0',
        },
    ]
    mocker.patch(
        'connect.cli.core.utils.subprocess.check_output',
        return_value=json.dumps(pip_resp),
    )

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' in captured.out
    assert 'A newer version is available: 2.0.0' in captured.out


def test_check_for_updates_ko_name(mocker, capsys):
    pip_resp = [
        {
            'name': 'connect-client',
            'version': '1.0.0',
            'latest_version': '2.0.0',
        },
    ]
    mocker.patch(
        'connect.cli.core.utils.subprocess.check_output',
        return_value=json.dumps(pip_resp),
    )

    utils.check_for_updates()

    captured = capsys.readouterr()
    assert captured.out == ''


def test_check_for_updates_ko_call(mocker, capsys):
    mocker.patch(
        'connect.cli.core.utils.subprocess.check_output',
        side_effect=subprocess.CalledProcessError('error', []),
    )

    utils.check_for_updates()

    captured = capsys.readouterr()
    assert captured.out == ''
