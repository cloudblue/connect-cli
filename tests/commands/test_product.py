from click.testing import CliRunner

from cnctcli.ccli import cli


def test_export(config_mocker, mocker):
    mock = mocker.patch(
        'cnctcli.commands.product.dump_product',
        side_effect=lambda *args: 'PRD-000.xlsx',
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'product',
            'export',
            'PRD-000',
        ],
    )
    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'PRD-000'
    assert mock.mock_calls[0][1][3] is None
    assert result.exit_code == 0
    assert 'The product PRD-000 has been successfully exported to PRD-000.xlsx.\n' in result.output


def test_export_custom_file(config_mocker, mocker):
    mock = mocker.patch(
        'cnctcli.commands.product.dump_product',
        side_effect=lambda *args: '/tmp/my_product.xlsx',
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            'product',
            'export',
            'PRD-000',
            '-o',
            '/tmp/my_product.xlsx'
        ],
    )
    mock.assert_called_once()
    assert mock.mock_calls[0][1][2] == 'PRD-000'
    assert mock.mock_calls[0][1][3] == '/tmp/my_product.xlsx'
    assert result.exit_code == 0
    assert 'The product PRD-000 has been successfully exported to /tmp/my_product.xlsx.\n' \
        in result.output
