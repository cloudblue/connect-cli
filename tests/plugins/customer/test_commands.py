import pytest
from click.testing import CliRunner


def test_export_customers(mocker, config_mocker, ccli):
    mocked_dump = mocker.patch(
        'connect.cli.plugins.customer.commands.dump_customers',
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'customer',
            'export',
        ],
    )

    assert result.exit_code == 0
    mocked_dump.assert_called_once()


@pytest.mark.parametrize('filename', ('customers', 'customers.xlsx'))
def test_sync_customers(mocker, config_mocker, ccli, filename):
    mocked_sync = mocker.MagicMock()
    mocker.patch(
        'connect.cli.plugins.customer.commands.CustomerSynchronizer',
        return_value=mocked_sync,
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'customer',
            'sync',
            filename,
        ],
    )

    assert result.exit_code == 0
    mocked_sync.open.assert_called_once()
    mocked_sync.sync.assert_called_once()
    mocked_sync.save.assert_called_once()
    mocked_sync.stats.print.assert_called_once()
