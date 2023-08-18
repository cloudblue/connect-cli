import json
import tempfile
import os
from copy import copy, deepcopy

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


@pytest.mark.parametrize('validate', (True, False))
@pytest.mark.parametrize('stream_type', ('Computed', 'Simple'))
def test_clone_stream(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
    stream_type,
    validate,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json={},
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json={},
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        if stream_type == 'Computed':
            del response['samples']
            response['sources'] = {'something': 'else'}
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams',
        json={'id': 'STR-4444-5555-6666'},
    )
    if stream_type == 'Simple':
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/media/folders/streams_samples/STR-7755-7115-2464/files/MFL-9059-7665-2037',
            body=b'somecontent',
        )
        mocked_responses.add(
            method='POST',
            url='https://localhost/public/v1/media/folders/streams_samples/STR-4444-5555-6666/files',
            json={'id': 'MFL-9059-7665-333'},
        )
        mocked_responses.add(
            method='PUT',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666',
            json={'samples': {'input': {'id': 'MFL-9059-7665-333'}}},
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
        method='POST',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-4444-5555-6666/files',
        json={'id': 'MFL-9059-7665-444'},
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files/MFL-8784-6884-8192',
        body=b'somecontent',
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-4444-5555-6666/files',
        json={'id': 'MFL-9059-7665-555'},
    )

    with open('./tests/fixtures/commerce/columns_response.json') as content:
        data = json.load(content)
        last_column = data[-1]
        last_column['id'] = 'SCOL-7755-7115-2464-011'
        last_column['position'] = 110000
        data.append(last_column)
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/columns?limit=100&offset=0',
            json=data,
        )

    with open('./tests/fixtures/commerce/transformations_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
            json=json.load(content),
        )

    with open('./tests/fixtures/commerce/columns_response.json') as content:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/columns?limit=100&offset=0',
            json=json.load(content),
        )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/transformations',
    )

    with open('./tests/fixtures/commerce/columns_response.json') as content:
        data = json.load(content)
        last_column = data[-1]
        last_column['id'] = 'SCOL-7755-7115-2464-011'
        last_column['position'] = 110000
        data.append(last_column)
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/columns?limit=100&offset=0',
            json=data,
        )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/transformations',
    )

    with open('./tests/fixtures/commerce/columns_response.json') as content:
        data = json.load(content)
        updated_data = deepcopy(data)
        updated_data[9]['output'] = False
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/columns?limit=100&offset=0',
            json=updated_data,
        )
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/columns?limit=100&offset=0',
            json=data,
        )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/columns/SCOL-7755-7115-2464-010',
        json={'output': False},
    )

    if validate:
        mocked_responses.add(
            method='POST',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/validate',
        )

    mocker.patch('connect.cli.plugins.commerce.utils.console')
    mocked_cmd_console = mocker.patch(
        'connect.cli.plugins.commerce.commands.console',
    )
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            'commerce',
            'stream',
            'clone',
            'STR-7755-7115-2464',
        ]
        if validate:
            cmd.append('-v')
        result = runner.invoke(
            ccli,
            cmd,
        )

    assert result.exit_code == 0
    assert mocked_cmd_console.echo.call_count == 3
    mocked_cmd_console.confirm.assert_called_with(
        'Are you sure you want to Clone ' f'the stream STR-7755-7115-2464 ?',
        abort=True,
    )
    mocked_cmd_console.secho.assert_called_with(
        f'Stream STR-7755-7115-2464 cloned properly to STR-4444-5555-6666.',
        fg='green',
    )


def test_clone_computed_stream_empty_attachments_and_transformations(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
):
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        del response['samples']
        response['sources'] = {'something': 'else'}
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams',
        json={'id': 'STR-4444-5555-6666'},
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files?limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
        json=[],
    )

    with open('./tests/fixtures/commerce/columns_response.json') as content:
        data = json.load(content)
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/columns?limit=100&offset=0',
            json=data,
        )
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams/STR-4444-5555-6666/columns?limit=100&offset=0',
            json=data,
        )

    mocked_utils_console = mocker.patch('connect.cli.plugins.commerce.utils.console')
    mocker.patch(
        'connect.cli.plugins.commerce.utils.guess_if_billing_or_pricing_stream',
        return_value='pricing',
    )

    mocked_cmd_console = mocker.patch(
        'connect.cli.plugins.commerce.commands.console',
    )

    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            'commerce',
            'stream',
            'clone',
            'STR-7755-7115-2464',
        ]
        result = runner.invoke(
            ccli,
            cmd,
        )

    assert result.exit_code == 0
    assert mocked_cmd_console.echo.call_count == 3
    mocked_cmd_console.confirm.assert_called_with(
        'Are you sure you want to Clone ' f'the stream STR-7755-7115-2464 ?',
        abort=True,
    )
    mocked_cmd_console.secho.assert_called_with(
        f'Stream STR-7755-7115-2464 cloned properly to STR-4444-5555-6666.',
        fg='green',
    )


def test_clone_destination_account(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
):
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products?eq(id,PRD-054-258-626)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/marketplaces?eq(id,MP-05011)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/accounts?eq(id,PA-050-101)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricelists?eq(id,PL-123)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams',
        json={'id': 'STR-4444-5555-6666'},
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files?limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
        json=[],
    )

    mocked_utils_console = mocker.patch('connect.cli.plugins.commerce.utils.console')
    mocker.patch(
        'connect.cli.plugins.commerce.utils.guess_if_billing_or_pricing_stream',
        return_value='pricing',
    )
    mocker.patch(
        'connect.cli.plugins.commerce.utils.clone_sample',
    )
    mocker.patch(
        'connect.cli.plugins.commerce.utils.align_column_output',
        return_value=(0, 0),
    )
    mocked_cmd_console = mocker.patch(
        'connect.cli.plugins.commerce.commands.console',
    )

    runner = CliRunner()
    with tempfile.TemporaryDirectory():
        cmd = [
            'commerce',
            'stream',
            'clone',
            'STR-7755-7115-2464',
            '-d',
            'VA-001',
        ]
        result = runner.invoke(
            ccli,
            cmd,
        )

    assert result.exit_code == 0
    assert mocked_cmd_console.echo.call_count == 3
    mocked_cmd_console.confirm.assert_called_with(
        'Are you sure you want to Clone ' f'the stream STR-7755-7115-2464 ?',
        abort=True,
    )
    mocked_cmd_console.secho.assert_called_with(
        f'Stream STR-7755-7115-2464 cloned properly to STR-4444-5555-6666.',
        fg='green',
    )
    mocked_utils_console.progress.assert_called()


def test_clone_destination_account_objects_not_found(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
):
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products?eq(id,PRD-054-258-626)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/marketplaces?eq(id,MP-05011)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/accounts?eq(id,PA-050-101)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricelists?eq(id,PL-123)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/pricing/streams',
        json={'id': 'STR-4444-5555-6666'},
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7755-7115-2464/files?limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams/STR-7755-7115-2464/transformations?limit=100&offset=0',
        json=[],
    )

    mocked_utils_console = mocker.patch('connect.cli.plugins.commerce.utils.console')
    mocker.patch(
        'connect.cli.plugins.commerce.utils.guess_if_billing_or_pricing_stream',
        return_value='pricing',
    )
    mocker.patch(
        'connect.cli.plugins.commerce.utils.clone_sample',
    )
    mocker.patch(
        'connect.cli.plugins.commerce.utils.align_column_output',
        return_value=(0, 0),
    )
    mocked_cmd_console = mocker.patch(
        'connect.cli.plugins.commerce.commands.console',
    )

    runner = CliRunner()
    with tempfile.TemporaryDirectory():
        cmd = [
            'commerce',
            'stream',
            'clone',
            'STR-7755-7115-2464',
            '-d',
            'VA-001',
        ]
        result = runner.invoke(
            ccli,
            cmd,
        )

    assert result.exit_code == 0
    assert mocked_cmd_console.echo.call_count == 3
    mocked_cmd_console.confirm.assert_called_with(
        'Are you sure you want to Clone ' f'the stream STR-7755-7115-2464 ?',
        abort=True,
    )
    mocked_cmd_console.secho.assert_called_with(
        f'Stream STR-7755-7115-2464 cloned properly to STR-4444-5555-6666.',
        fg='green',
    )
    mocked_utils_console.progress.assert_called()
    assert mocked_utils_console.secho.call_count == 4
    call_args = mocked_utils_console.secho.call_args_list
    assert call_args[0] == mocker.call(
        'The product PRD-054-258-626 does not exists.',
        fg='yellow',
    )
    assert call_args[1] == mocker.call(
        'The marketplace MP-05011 does not exists.',
        fg='yellow',
    )
    assert call_args[2] == mocker.call(
        'The account PA-050-101 does not exists.',
        fg='yellow',
    )
    assert call_args[3] == mocker.call(
        'The pricelist PL-123 does not exists.',
        fg='yellow',
    )


def test_clone_destination_account_not_found(
    ccli,
    config_mocker,
):
    runner = CliRunner()
    with tempfile.TemporaryDirectory():
        cmd = [
            'commerce',
            'stream',
            'clone',
            'STR-7755-7115-2464',
            '-d',
            'VA-666',
        ]
        result = runner.invoke(
            ccli,
            cmd,
        )

    assert result.exit_code == 1
    assert result.output == (
        'Current active account: VA-000 - Account 0\n\nError: Error obtaining the destination account id VA-666\n'
    )


def test_sync_stream(
    mocker,
    ccli,
    mocked_responses,
    config_mocker,
    load_stream_sync,
):
    mocked_get_work_book = mocker.patch(
        'connect.cli.plugins.commerce.utils.get_work_book',
        return_value=load_stream_sync,
    )
    mocked_upload_attachment = mocker.patch(
        'connect.cli.plugins.commerce.utils.upload_attachment',
        return_value={'id': 'ID'},
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-7748-7021-7449)&limit=0&offset=0',
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )

    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/billing/streams?eq(id,STR-7748-7021-7449)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449',
        json=[],
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations/STRA-774-870-217-449-001',
        json={'settings': {'some': 'settings'}, 'description': 'description', 'position': 50},
    )
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations/STRA-774-870-217-449-001',
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations/STRA-774-870-217-449-002',
        json={'settings': {'some': 'settings'}, 'description': 'description', 'position': 60},
    )
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations/STRA-774-870-217-449-002',
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations',
        json=[
            {'id': 'STRA-774-870-217-449-001'},
            {'id': 'STRA-774-870-217-449-002'},
            {'id': 'STRA-774-870-217-449-003'},
        ],
    )
    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/billing/streams/STR-7748-7021-7449/transformations/STRA-774-870-217-449-003',
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7748-7021-7449/files?eq(id,ID)&limit=0&offset=0',
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7748-7021-7449/files?eq(id,ID-EXISTS)&limit=0&offset=0',
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7748-7021-7449/files?limit=100&offset=0',
        json=[{'id': 'ID-EXISTS'}, {'id': 'DO-NOT-EXIST'}],
    )
    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/media/folders/streams_attachments/STR-7748-7021-7449/files/DO-NOT-EXIST',
        status=204,
    )

    mocked_cmd_console = mocker.patch(
        'connect.cli.plugins.commerce.commands.console',
    )
    runner = CliRunner()
    cmd = [
        'commerce',
        'stream',
        'sync',
        'STR-7748-7021-7449',
    ]
    result = runner.invoke(
        ccli,
        cmd,
    )

    mocked_upload_attachment.assert_called_with(
        mocker.ANY,
        'STR-7748-7021-7449',
        'STR-7748-7021-7449/attachments/attachment.xlsx',
    )

    assert result.exit_code == 0
    assert mocked_cmd_console.echo.call_count == 2
