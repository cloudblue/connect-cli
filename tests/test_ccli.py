import click

from connect.cli.ccli import main
from connect.cli.core.constants import CAIRO_NOT_FOUND_ERROR


def test_run_ok(mocker):
    mock_cli = mocker.patch('connect.cli.ccli.cli')
    mock_load_plugins = mocker.patch('connect.cli.ccli.load_plugins')

    main()
    mock_load_plugins.assert_called_once_with(mock_cli)
    mock_cli.assert_called_once_with(prog_name='ccli', standalone_mode=False)


def test_run_click_exception(mocker):
    mock_cli = mocker.patch('connect.cli.ccli.cli', side_effect=click.ClickException('test exc'))
    mock_load_plugins = mocker.patch('connect.cli.ccli.load_plugins')
    mock_secho = mocker.patch('connect.cli.ccli.click.secho')
    main()
    mock_load_plugins.assert_called_once_with(mock_cli)
    mock_cli.assert_called_once_with(prog_name='ccli', standalone_mode=False)
    mock_secho.assert_called_once_with('test exc', fg='red')


def test_run_abort_exception(mocker):
    mock_cli = mocker.patch('connect.cli.ccli.cli', side_effect=click.exceptions.Abort('abort'))
    mock_load_plugins = mocker.patch('connect.cli.ccli.load_plugins')
    mock_secho = mocker.patch('connect.cli.ccli.click.secho')
    main()
    mock_load_plugins.assert_called_once_with(mock_cli)
    mock_cli.assert_called_once_with(prog_name='ccli', standalone_mode=False)
    mock_secho.assert_not_called()


def test_run_no_cairo(mocker):
    mocker.patch(
        'connect.cli.ccli.cli',
        side_effect=OSError('no library called "cairo" was found'),
    )
    mocker.patch('connect.cli.ccli.load_plugins')
    mock_secho = mocker.patch('connect.cli.ccli.click.secho')

    main()
    mock_secho.assert_called_once_with(CAIRO_NOT_FOUND_ERROR, fg='yellow')


def test_run_other_os_error(mocker):
    mocker.patch(
        'connect.cli.ccli.cli',
        side_effect=OSError('other error'),
    )
    mocker.patch('connect.cli.ccli.load_plugins')
    mock_secho = mocker.patch('connect.cli.ccli.click.secho')

    main()
    mock_secho.assert_called_once_with('other error', fg='red')
