import json
import tempfile
import os

import pytest
from click.testing import CliRunner


def test_list_streams(mocker, ccli, mocked_responses, config_mocker):
    mocked_table = mocker.patch('connect.cli.plugins.commerce.utils.console.table')
    with open('./tests/fixtures/commerce/billing_streams_response.json') as bsresponse:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/billing/streams?select(context,sources)&limit=25&offset=0',
            json=json.load(bsresponse),
        )
    with open('./tests/fixtures/commerce/pricing_streams_response.json') as psresponse:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?select(context,sources)&limit=25&offset=0',
            json=json.load(psresponse),
        )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        ['commerce', 'stream', 'list'],
    )
    assert result.exit_code == 0

    mocked_table.assert_called_with(
        columns=[
            'ID',
            'Business scope',
            'Name',
            'Type',
            'Category',
            'Status',
            'Visibility',
        ],
        rows=[
            (
                'STR-6250-2064-0382',
                'Billing',
                'My simple billing from source',
                'Computed',
                'Inbound',
                'Configuring',
                'Private',
            ),
            (
                'STR-7755-0103-9379',
                'Billing',
                'My simple billing stream',
                'Simple',
                'Outbound',
                'Active',
                'Private',
            ),
            (
                'STR-8722-8683-0414',
                'Billing',
                'Simple Billing stream',
                'Simple',
                'Inbound',
                'Active',
                'Published',
            ),
            (
                'STR-4047-7247-4594',
                'Pricing',
                'My simple pricing stream',
                'Simple',
                'Outbound',
                'Configuring',
                'Private',
            ),
            (
                'STR-5066-5885-2990',
                'Pricing',
                'My computed pricing from pricing stream',
                'Computed',
                'Inbound',
                'Active',
                'Private',
            ),
            (
                'STR-7755-7115-2464',
                'Pricing',
                'Simple pricing stream',
                'Simple',
                'Inbound',
                'Active',
                'Published',
            ),
        ],
    )


def test_list_streams_empty(mocker, ccli, mocked_responses, config_mocker):
    mocked_secho = mocker.patch('connect.cli.plugins.commerce.utils.console.secho')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?select(context,sources)&limit=25&offset=0',
        json=[],
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams?select(context,sources)&limit=25&offset=0',
        json=[],
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        ['commerce', 'stream', 'list'],
    )
    assert result.exit_code == 0

    mocked_secho.assert_called_with(
        f'Results not found for the current account VA-000.',
        fg='yellow',
    )


def test_export_stream_not_found(mocker, ccli, mocked_responses, config_mocker):
    mocked_secho = mocker.patch('connect.cli.plugins.commerce.utils.console.secho')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-123)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams?eq(id,STR-123)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )

    runner = CliRunner()
    result = runner.invoke(
        ccli,
        [
            'commerce',
            'stream',
            'export',
            'STR-123',
        ],
    )

    assert result.exit_code == 0
    mocked_secho.assert_called_with(
        f'Stream STR-123 not found for the current account VA-000.',
        fg='red',
    )


@pytest.mark.parametrize('create_sample_input', (True, False))
@pytest.mark.parametrize('create_attachments', (True, False))
def test_export_stream_pricing(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
    create_attachments,
    create_sample_input,
):
    mocker.patch(
        'connect.cli.plugins.commerce.utils.guess_if_billing_or_pricing_stream',
        return_value='pricing',
    )
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=json.load(content),
        )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_samples/STR-7755-7115-2464/files/MFL-9059-7665-2037',
        body=b'somecontent',
    )
    with open('./tests/fixtures/commerce/columns_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/columns?limit=100&offset=0',
            json=json.load(content),
        )
    with open('./tests/fixtures/commerce/transformations_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
            json=json.load(content),
        )
    with open('./tests/fixtures/commerce/attachments_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files?limit=100&offset=0',
            json=json.load(content),
        )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files/MFL-2481-0572-9001',
        body=b'somecontent',
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files/MFL-8784-6884-8192',
        body=b'somecontent',
    )

    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        mocker.patch('os.getcwd', return_value=tmpdir)
        if create_attachments:
            os.mkdir(os.path.join(tmpdir, 'attachments'))
        if create_sample_input:
            os.makedirs(os.path.join(tmpdir, 'sample', 'input'))
        mocked_output = mocker.patch(
            'connect.cli.plugins.commerce.utils.validate_output_options',
            return_value=os.path.join(tmpdir, 'STR-7755-7115-2464.xlsx'),
        )
        result = runner.invoke(
            ccli,
            [
                'commerce',
                'stream',
                'export',
                'STR-7755-7115-2464',
            ],
        )
        mocked_output.assert_called_with(None, None, default_dir_name='STR-7755-7115-2464')

    assert result.exit_code == 0


def test_export_stream_transformations_client_error(mocker, ccli, mocked_responses, config_mocker):
    mocker.patch('connect.cli.plugins.commerce.utils.console.secho')
    mocker.patch(
        'connect.cli.plugins.commerce.utils.guess_if_billing_or_pricing_stream',
        return_value='pricing',
    )
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=json.load(content),
        )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_samples/STR-7755-7115-2464/files/MFL-9059-7665-2037',
        body=b'somecontent',
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/columns?limit=100&offset=0',
        json=[],
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
        status=404,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files?limit=100&offset=0',
        json=[],
    )

    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        mocker.patch('os.getcwd', return_value=tmpdir)
        result = runner.invoke(
            ccli,
            [
                'commerce',
                'stream',
                'export',
                'STR-7755-7115-2464',
            ],
        )

    assert result.exit_code == 0
