import click

from connect.cli.ccli import main


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
