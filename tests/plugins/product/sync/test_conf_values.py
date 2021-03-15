from connect.cli.plugins.product.sync.configuration_values import ConfigurationValuesSynchronizer
from connect.client import ConnectClient


def test_skipped(get_sync_config_env):

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/configuration_sync.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 1
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_validate_no_id(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = None
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['ID is required for update operation']}


def test_validate_wrong_id_format(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'test#'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['ID is not properly formatted']}


def test_validate_wrong_id_format2(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'test## !'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['ID is not properly formatted']}


def test_validate_update_no_value(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['I2'] = None
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Value is required for update operation']}


def test_validate_invalid_action(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'rocket'
    get_sync_config_env['Configuration']['I2'] = None
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Action can be either `-` or `update`, provided rocket']}


def test_validate_invalid_scope_param(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['B2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Parameter does not match configuration ID']}


def test_validate_invalid_scope_item(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['E2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Item does not match configuration ID']}


def test_validate_invalid_scope_marketplace(fs, get_sync_config_env):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['G2'] = 'a'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Marketplace does not match configuration ID']}


def test_update(fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            "ok": "ok",
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert deleted == 0
    assert errors == {}


def test_update_json(fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'update'
    get_sync_config_env['Configuration']['I2'] = '{"key": "val"}'

    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            "ok": "ok",
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert deleted == 0
    assert errors == {}


def test_delete(fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'delete'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        json={
            "ok": "ok",
        },
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_500(fs, get_sync_config_env, mocked_responses):
    get_sync_config_env['Configuration']['A2'] = 'asdf#PRD-276-377-545-0001#MKP-123'
    get_sync_config_env['Configuration']['G2'] = 'MKP-123'
    get_sync_config_env['Configuration']['D2'] = 'delete'
    get_sync_config_env.save(f'{fs.root_path}/test.xlsx')

    synchronizer = ConfigurationValuesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/configurations',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}
