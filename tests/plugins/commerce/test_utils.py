import os
import tempfile

import pytest
from click import ClickException
from openpyxl import Workbook

from connect.cli.plugins.commerce.utils import (
    fill_and_download_attachments,
    guess_if_billing_or_pricing_stream,
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
