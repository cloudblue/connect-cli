from connect.client import ConnectClient

from connect.cli.plugins.product.sync.configuration_values import ConfigurationValuesSynchronizer
from connect.cli.plugins.shared.sync_stats import SynchronizerStats


def test_skipped(mocker, get_sync_config_env):
    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/configuration_sync.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 1,
        'errors': 0,
    }


def test_validate_no_id(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = None
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['ID is required for update operation']}


def test_validate_wrong_id_format(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'test#'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['ID is not properly formatted']}


def test_validate_wrong_id_format2(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'test## !'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['ID is not properly formatted']}


def test_validate_update_no_value(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['I2'] = None
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['Value is required for update operation']}


def test_validate_invalid_action(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'rocket'
    get_sync_config_env['Configuration']['I2'] = None
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {
        2: ['Action can be either `-` or `update`, provided rocket'],
    }


def test_validate_invalid_scope_param(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['B2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['Parameter does not match configuration ID']}


def test_validate_invalid_scope_item(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['E2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['Item does not match configuration ID']}


def test_validate_invalid_scope_marketplace(mocker, fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['G2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {
        2: ['Marketplace does not match configuration ID'],
    }


def test_update(mocker, fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            'ok': 'ok',
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }


def test_update_json(mocker, fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['I2'] = '{"key": "val"}'

    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            'ok': 'ok',
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }


def test_delete(mocker, fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'delete'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            'ok': 'ok',
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 1,
        'skipped': 0,
        'errors': 0,
    }


def test_delete_500(mocker, fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'delete'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')
    synchronizer.sync()

    assert stats['Configuration'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Configuration']._row_errors == {2: ['500 Internal Server Error']}
