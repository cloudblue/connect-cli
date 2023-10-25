from copy import deepcopy

import pytest
from connect.client import ConnectClient

from connect.cli.plugins.product.sync.capabilities import CapabilitiesSynchronizer
from connect.cli.plugins.shared.sync_stats import SynchronizerStats


def test_no_action(mocker, get_sync_capabilities_env):
    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/capabilities_sync.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 10,
        'errors': 0,
    }


def test_invalid_capability(mocker, fs, get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['A2'].value = 'Invented'
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {2: ['Capability Invented is not valid capability']}


def test_invalid_usage_schema(mocker, fs, get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C2'].value = 'magic'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {2: ['Schema magic is not supported']}


def test_invalid_tier_level(mocker, fs, get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B9'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C9'].value = 'magic'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {
        9: ['magic is not valid for Reseller Authorization level capability'],
    }


def test_invalid_value(mocker, fs, get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B11'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C11'].value = 'magic'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {
        11: ['Administrative Hold may be Enabled or Disabled, but not magic'],
    }


def test_ppu_enable_qt(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C2'].value = 'QT'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_change_schema(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C2'].value = 'TR'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_disable(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C2'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_dynamic_items_no_ppu(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C3'].value = 'Enabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {
        3: ["Dynamic items support can't be enabled without Pay-as-you-go support"],
    }


def test_ppu_dynamic_items_no_ppu_no_enabled(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C3'].value = 'Disabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_enable_dynamic(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C3'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_disable_dynamic(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C3'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_future_no_ppu(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C4'].value = 'Enabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {
        4: ["Report of future charges can't be enabled without Pay-as-you-go support"],
    }


def test_ppu_future_no_ppu_no_enabled(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C4'].value = 'Disabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_enable_future(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C4'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_disable_future(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C4'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_late_no_ppu(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B5'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C5'].value = 'Enabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 9,
        'errors': 1,
    }
    assert stats['Capabilities']._row_errors == {
        5: ["Report of late charges can't be enabled without Pay-as-you-go support"],
    }


def test_ppu_late_no_ppu_no_enabled(
    mocker,
    fs,
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B5'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C5'].value = 'Disabled'
    get_sync_capabilities_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_enable_late(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B5'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C5'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


def test_ppu_disable_late(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B5'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C5'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


@pytest.mark.parametrize(
    ('row_action',),
    (
        (6,),
        (7,),
        (8,),
        (9,),
        (10,),
        (11,),
    ),
)
def test_features_disable_feature(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    row_action,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'B{row_action}'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'C{row_action}'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


@pytest.mark.parametrize(
    ('row_action',),
    (
        (6,),
        (7,),
        (8,),
        (10,),
        (11,),
    ),
)
def test_features_enable_feature(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    row_action,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'B{row_action}'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'C{row_action}'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }


@pytest.mark.parametrize(
    ('tier_level',),
    (
        (1,),
        (2,),
    ),
)
def test_tier_level_feature(
    mocker,
    fs,
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    tier_level,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B9'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C9'].value = tier_level
    get_sync_capabilities_env_ppu_enabled.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Capabilities')
    synchronizer.sync()

    assert stats['Capabilities'].get_counts_as_dict() == {
        'processed': 10,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 9,
        'errors': 0,
    }
