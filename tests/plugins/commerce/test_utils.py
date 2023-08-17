import os
import tempfile
import json

import pytest
from click import ClickException
from openpyxl import Workbook

from connect.cli.plugins.commerce.utils import (
    fill_and_download_attachments,
    guess_if_billing_or_pricing_stream,
    clone_stream,
    create_stream_from_origin,
    clone_transformations,
)


def test_guess_if_billing_or_pricing_billing(mocked_responses, client):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-123)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    assert guess_if_billing_or_pricing_stream(client, 'STR-123') == 'billing'


def test_guess_if_billing_or_pricing_pricing(mocked_responses, client):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-567)&limit=0&offset=0',
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
            'Content-Range': 'items 0-1/1',
        },
    )
    assert guess_if_billing_or_pricing_stream(client, 'STR-123') == 'pricing'


def test_guess_if_billing_or_pricing_none(mocked_responses, client):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-567)&limit=0&offset=0',
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
    assert guess_if_billing_or_pricing_stream(client, 'STR-123') is None


def test_fill_attachments_download_fails(mocked_responses, mocker, client):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/media/folders/ftype/fname/files/id',
        status=500,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        wb = Workbook()
        ws = wb.create_sheet('Attachments')
        mocked_progress = mocker.MagicMock()
        with pytest.raises(ClickException) as exc:
            fill_and_download_attachments(
                ws,
                [
                    {
                        'id': 'id',
                        'name': 'name',
                        'folder': {'type': 'ftype', 'name': 'fname'},
                    },
                ],
                client,
                os.path.join(tmpdir, 'media'),
                mocked_progress,
            )
            assert exec.value == 'Error obtaining file name'


def test_clone_stream_not_found(
    mocker,
    mocked_responses,
    client,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/pricing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )

    with pytest.raises(ClickException) as e:
        clone_stream(
            mocker.MagicMock(client=client, id='VA-000'),
            'STR-7755-7115-2464',
            None,
        )

    assert str(e.value) == 'Stream STR-7755-7115-2464 not found for the current account VA-000.'


def test_clone_stream_computed_and_diff_accounts(
    mocker,
    mocked_responses,
    client,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        response['sources'] = {'some': 'thing'}
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )

    with pytest.raises(ClickException) as e:
        clone_stream(
            mocker.MagicMock(client=client, id='VA-000'),
            'STR-7755-7115-2464',
            mocker.MagicMock(client=client, id='VA-001'),
        )

    assert str(e.value) == 'You cannot clone a Computed stream between different accounts.'


def test_clone_inbound_stream(
    mocker,
    mocked_responses,
    client,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    with open('./tests/fixtures/commerce/stream_retrieve_response.json') as content:
        response = json.load(content)[0]
        response['owner']['id'] = 'VA-999'
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/billing/streams?eq(id,STR-7755-7115-2464)&select(context,samples,sources)&limit=1&offset=0',
            json=[response],
        )

    with pytest.raises(ClickException) as e:
        clone_stream(
            mocker.MagicMock(client=client, id='VA-000'),
            'STR-7755-7115-2464',
            mocker.MagicMock(client=client, id='VA-001'),
        )

    assert str(e.value) == 'Inbound streams cannot be cloned.'


def test_create_stream_from_origin_error(
    mocked_responses,
    client,
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/billing/streams',
        status=400,
        json={'error_code': 'error_code', 'errors': ['error one']},
    )
    with pytest.raises(ClickException) as e:
        create_stream_from_origin(
            client,
            {
                'id': 'STR-123',
                'context': {},
                'name': 'name',
                'sources': [],
                'owner': {'id': 'VA-000'},
            },
            'billing',
        )
    assert str(e.value) == 'error one'


def test_clone_transformations_with_two_columns_same_name(
    mocker,
):
    mocked_col_mapping = mocker.patch(
        'connect.cli.plugins.commerce.utils.generate_column_mapping',
        return_value=({'name': ['COL-ID-1', 'COL-ID-2']}, {'COL-ID-1': '', 'COL-ID-2': ''}),
    )
    mocked_progress = mocker.MagicMock()
    clone_transformations(
        mocker.MagicMock(),
        'STR-333',
        'billing',
        {},
        [
            {
                'function': {'id': 'fn-123', 'name': 'Lookup Data from a stream attached Excel'},
                'settings': {},
                'overview': 'overview',
                'position': 1000,
                'columns': {'input': [{'id': 'COL-ID-2', 'name': 'name'}], 'output': []},
            },
        ],
        {'name': ['COL-ID-1', 'COL-ID-2']},
        mocked_progress,
    )
    mocked_col_mapping.assert_called()
    mocked_progress.add_task.assert_called_with('Processing transformations', total=1)
    assert mocked_progress.update.call_count == 1


def test_clone_transformations_fix_file_mapping(
    mocker,
    client,
    mocked_responses,
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/billing/streams/STR-333/transformations',
    )
    mocked_col_mapping = mocker.patch(
        'connect.cli.plugins.commerce.utils.generate_column_mapping',
        return_value=({'name': ['COL-ID-1', 'COL-ID-2']}, {'COL-ID-1': '', 'COL-ID-2': ''}),
    )
    mocked_progress = mocker.MagicMock()
    clone_transformations(
        client,
        'STR-333',
        'billing',
        {'filepath': 'newfilepath'},
        [
            {
                'function': {'id': 'fn-123', 'name': 'Lookup Data from a stream attached Excel'},
                'settings': {'file': 'filepath'},
                'overview': 'overview',
                'position': 1000,
                'columns': {'input': [{'id': 'COL-ID-2', 'name': 'name'}], 'output': []},
            },
        ],
        {'name': ['COL-ID-1', 'COL-ID-2']},
        mocked_progress,
    )
    mocked_col_mapping.assert_called()
    mocked_progress.add_task.assert_called_with('Processing transformations', total=1)
    assert mocked_progress.update.call_count == 1
