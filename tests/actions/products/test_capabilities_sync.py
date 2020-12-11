from cnctcli.actions.products.capabilities_sync import CapabilitiesSynchronizer
from cnct import ConnectClient
from copy import deepcopy

import pytest


def test_no_action(get_sync_capabilities_env):
    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/capabilities_sync.xlsx', 'Capabilities')
    skipped, updated, errors = synchronizer.sync()

    assert skipped == 9
    assert updated == 0
    assert errors == {}


def test_invalid_capability(get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['A2'].value = 'Invented'
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {2: ['Capability Invented is not valid capability']}


def test_invalid_usage_schema(get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C2'].value = 'magic'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {2: ['Schema magic is not supported']}


def test_invalid_tier_level(get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B8'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C8'].value = 'magic'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {8: ['magic is not valid for Reseller Authorization level capability']}


def test_invalid_value(get_sync_capabilities_env):
    get_sync_capabilities_env['Capabilities']['B10'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C10'].value = 'magic'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {10: ['Administrative Hold may be Enabled or Disabled, but not magic']}


def test_ppu_enable_qt(
    get_sync_capabilities_env,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C2'].value = 'QT'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_change_schema(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C2'].value = 'TR'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_disable(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B2'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C2'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_dynamic_items_no_ppu(
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C3'].value = 'Enabled'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {3: ["Dynamic items support can't be enabled without Pay-as-you-go support"]}


def test_ppu_dynamic_items_no_ppu_no_enabled(
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C3'].value = 'Disabled'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_enable_dynamic(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C3'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_disable_dynamic(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B3'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C3'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_future_no_ppu(
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C4'].value = 'Enabled'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 0
    assert errors == {
        4: ["Report of future charges can't be enabled without Pay-as-you-go support"]
    }


def test_ppu_future_no_ppu_no_enabled(
    get_sync_capabilities_env,
    mocked_responses,
):
    get_sync_capabilities_env['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env['Capabilities']['C4'].value = 'Disabled'
    get_sync_capabilities_env.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_enable_future(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C4'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


def test_ppu_disable_future(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities']['B4'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities']['C4'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    response = deepcopy(mocked_product_response)
    response['capabilities']['ppu'] = {
        'schema': 'QT',
    }

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


@pytest.mark.parametrize(
    ('row_action',),
    (
        (5,),
        (6,),
        (7,),
        (8,),
        (9,),
        (10,),
    ),
)
def test_ppu_disable_feature(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    row_action,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'B{row_action}'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'C{row_action}'].value = 'Disabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


@pytest.mark.parametrize(
    ('row_action',),
    (
        (5,),
        (6,),
        (7,),
        (9,),
        (10,),
    ),
)
def test_features_enable_future(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    row_action,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'B{row_action}'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'C{row_action}'].value = 'Enabled'
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}


@pytest.mark.parametrize(
    ('tier_level',),
    (
        (1,),
        (2,),
    ),
)
def test_tier_level_feature(
    get_sync_capabilities_env_ppu_enabled,
    mocked_responses,
    mocked_product_response,
    tier_level,
):
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'B8'].value = 'update'
    get_sync_capabilities_env_ppu_enabled['Capabilities'][f'C8'].value = tier_level
    get_sync_capabilities_env_ppu_enabled.save('./test.xlsx')

    synchronizer = CapabilitiesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response
    )

    synchronizer.open('./test.xlsx', 'Capabilities')

    skipped, updated, errors = synchronizer.sync()

    assert skipped == 8
    assert updated == 1
    assert errors == {}