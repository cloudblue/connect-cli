# -*- coding: utf-8 -*-

# This file is part of the CloudBlue Connect connect-cli.
# Copyright (c) 2025 CloudBlue. All Rights Reserved.

import pytest
from connect.client import ConnectClient

from connect.cli.plugins.product.sync.messages import MessageSynchronizer
from connect.cli.plugins.shared.sync_stats import SynchronizerStats


def test_message_sync(
    mocker,
    fs,
    get_sync_messages_env,
    mocked_responses,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0002',
        json={
            'id': 'PRDMSG-276-377-545-0002',
            'external_id': 'error2',
            'value': 'Error 2',
            'auto': True,
        },
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0002',
        json={
            'id': 'PRDMSG-276-377-545-0002',
            'external_id': 'error2',
            'value': 'Error 2',
            'auto': True,
        },
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0003',
        json={
            'id': 'PRDMSG-276-377-545-0003',
            'external_id': 'error3',
            'value': 'Error 3',
            'auto': True,
        },
    )
    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0003',
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages?eq(external_id,'
        'error2)&limit=1&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages',
        json={
            'id': 'PRDMSG-276-377-545-0004',
            'external_id': 'error4',
            'value': 'Error 4',
            'auto': True,
        },
    )

    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/messages_sync.xlsx', 'Messages')
    synchronizer.sync()

    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 1,
        'updated': 1,
        'deleted': 1,
        'skipped': 1,
        'errors': 0,
    }


def test_message_sync_with_errors(
    mocker,
    fs,
    get_sync_messages_env,
    mocked_responses,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0002',
        status=404,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0003',
        status=404,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages?eq(external_id,'
        'error2)&limit=1&offset=0',
        json=[
            {
                'id': 'PRDMSG-276-377-545-0004',
                'external_id': 'error4',
                'value': 'Error 4',
                'auto': True,
            }
        ],
    )

    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/messages_sync.xlsx', 'Messages')
    synchronizer.sync()

    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 1,
        'errors': 3,
    }
    assert (
        stats['Messages']._row_errors[3][0]
        == 'Cannot update message: message with ID `PRDMSG-276-377-545-0002` does not exist.'
    )
    assert (
        stats['Messages']._row_errors[4][0]
        == 'Cannot delete message: message with ID `PRDMSG-276-377-545-0003` does not exist.'
    )
    assert (
        stats['Messages']._row_errors[5][0]
        == 'Cannot create message: message with external_id `error4` already exists with ID `PRDMSG-276-377-545-0004`.'
    )


def test_message_sync_with_connection_error_on_update(
    mocker,
    fs,
    get_sync_messages_env,
    mocked_responses,
):
    get_sync_messages_env['Messages']['B4'].value = '-'
    get_sync_messages_env['Messages']['B5'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0002',
        json={
            'id': 'PRDMSG-276-377-545-0002',
            'external_id': 'error2',
            'value': 'Error 2',
            'auto': True,
        },
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0002',
        status=500,
    )

    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()

    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 3,
        'errors': 1,
    }
    assert stats['Messages']._row_errors[3][0] == '500 - Internal Server Error: unexpected error.'


def test_message_sync_with_connection_error_on_delete(
    mocker,
    fs,
    get_sync_messages_env,
    mocked_responses,
):
    get_sync_messages_env['Messages']['B3'].value = '-'
    get_sync_messages_env['Messages']['B5'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0003',
        json={
            'id': 'PRDMSG-276-377-545-0003',
            'external_id': 'error3',
            'value': 'Error 3',
            'auto': True,
        },
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages/PRDMSG-276-377-545-0003',
        status=500,
    )

    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()

    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 3,
        'errors': 1,
    }
    assert stats['Messages']._row_errors[4][0] == '500 - Internal Server Error: unexpected error.'


def test_message_sync_with_connection_error_on_create(
    mocker,
    fs,
    get_sync_messages_env,
    mocked_responses,
):
    get_sync_messages_env['Messages']['B3'].value = '-'
    get_sync_messages_env['Messages']['B4'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages?eq(external_id,'
        'error4)&limit=1&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/messages',
        status=500,
    )

    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()

    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 3,
        'errors': 1,
    }
    assert stats['Messages']._row_errors[5][0] == '500 - Internal Server Error: unexpected error.'


def test_messange_sync_validate_row_id_should_not_be(
    mocker,
    fs,
    get_sync_messages_env,
    client,
):
    get_sync_messages_env['Messages']['B2'].value = 'create'
    get_sync_messages_env['Messages']['B3'].value = '-'
    get_sync_messages_env['Messages']['B4'].value = '-'
    get_sync_messages_env['Messages']['B5'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')
    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=client,
        progress=mocker.MagicMock(),
        stats=stats,
    )
    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()
    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 3,
        'errors': 1,
    }
    assert (
        stats['Messages']._row_errors[2][0]
        == 'the `ID` must not be specified for the `create` action.'
    )


@pytest.mark.parametrize(
    'action',
    (
        'update',
        'delete',
    ),
)
def test_messange_sync_validate_row_id_should_be(
    mocker,
    fs,
    get_sync_messages_env,
    client,
    action,
):
    get_sync_messages_env['Messages']['A2'].value = ''
    get_sync_messages_env['Messages']['B2'].value = action
    get_sync_messages_env['Messages']['B3'].value = '-'
    get_sync_messages_env['Messages']['B4'].value = '-'
    get_sync_messages_env['Messages']['B5'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')
    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=client,
        progress=mocker.MagicMock(),
        stats=stats,
    )
    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()
    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 3,
        'errors': 1,
    }
    assert (
        stats['Messages']._row_errors[2][0]
        == 'the `ID` must be specified for the `update` or `delete` actions.'
    )


@pytest.mark.parametrize(
    'column',
    (
        'C',
        'D',
    ),
)
def test_messange_sync_validate_row_external_id_value_should_be(
    mocker,
    fs,
    get_sync_messages_env,
    client,
    column,
):
    get_sync_messages_env['Messages']['A2'].value = ''
    get_sync_messages_env['Messages']['B2'].value = 'create'
    get_sync_messages_env['Messages'][f'{column}2'].value = ''
    get_sync_messages_env['Messages']['B3'].value = 'update'
    get_sync_messages_env['Messages'][f'{column}3'].value = ''
    get_sync_messages_env['Messages']['B4'].value = 'delete'
    get_sync_messages_env['Messages'][f'{column}4'].value = ''
    get_sync_messages_env['Messages']['B5'].value = '-'
    get_sync_messages_env.save(f'{fs.root_path}/messages_sync.xlsx')
    stats = SynchronizerStats()
    synchronizer = MessageSynchronizer(
        client=client,
        progress=mocker.MagicMock(),
        stats=stats,
    )
    synchronizer.open(f'{fs.root_path}/messages_sync.xlsx', 'Messages')
    synchronizer.sync()
    assert stats['Messages'].get_counts_as_dict() == {
        'processed': 4,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 1,
        'errors': 3,
    }
    assert (
        stats['Messages']._row_errors[2][0]
        == 'the `External ID` and `Value` must be specified for the `create`, `update` or `delete` actions.'
    )
    assert (
        stats['Messages']._row_errors[3][0]
        == 'the `External ID` and `Value` must be specified for the `create`, `update` or `delete` actions.'
    )
    assert (
        stats['Messages']._row_errors[4][0]
        == 'the `External ID` and `Value` must be specified for the `create`, `update` or `delete` actions.'
    )
