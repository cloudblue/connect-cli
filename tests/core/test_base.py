from click.testing import CliRunner

from connect.cli.core.base import cli, print_version


def test_cli_confdir_exists(mocker, fs):
    mocked_makedirs = mocker.patch('connect.cli.core.base.os.makedirs')
    fs.makedir('.ccli')
    runner = CliRunner()
    runner.invoke(cli, ['-c', f'{fs.root_path}/.ccli', 'account', 'list'])
    mocked_makedirs.assert_not_called()


def test_cli_confdir_not_exists(mocker, fs):
    mocked_makedirs = mocker.patch('connect.cli.core.base.os.makedirs')
    runner = CliRunner()
    runner.invoke(cli, ['-c', f'{fs.root_path}/.ccli', 'account', 'list'])
    mocked_makedirs.assert_called_once_with(f'{fs.root_path}/.ccli')


def test_cli_print_version(mocker, capsys):
    mocker.patch('connect.cli.core.base.get_version', return_value='1.0.0')
    mocked = mocker.patch('connect.cli.core.base.check_for_updates')

    print_version(mocker.MagicMock(resilient_parsing=False), 'version', True)
    captured = capsys.readouterr()
    assert 'CloudBlue Connect CLI, version 1.0.0' in captured.out
    mocked.assert_called_once()
