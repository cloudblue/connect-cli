from connect.cli.core import utils
from connect.cli.core.constants import PYPI_JSON_API_URL


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


def test_check_for_updates_ok(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='1.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' in captured.out
    assert 'A newer version is available: 2.0.0' in captured.out


def test_check_for_updates_is_latest(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='2.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' not in captured.out
    assert 'A newer version is available: 2.0.0' not in captured.out
