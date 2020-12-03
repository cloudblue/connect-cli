from cnctcli.actions.products.items_sync import ItemSynchronizer
from cnct import ConnectClient
import pytest


def test_init(get_sync_items_env):

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    product_id = synchronizer.open('./tests/fixtures/items_sync.xlsx', 'Items')

    assert product_id == 'PRD-276-377-545'


def test_skipped(get_sync_items_env):

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/items_sync.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 1
    assert created == 0
    assert updated == 0
    assert errors == {}


@pytest.mark.parametrize(
    ('row_action',),
    (
        ("delete",),
        ("update",),
    ),
)
def test_validate_row_errors_no_row_id(get_sync_items_env, row_action):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['B2'].value = None
    get_sync_items_env['Items']['C2'].value = row_action
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: [f'one between the item `ID` or `MPN` is required for the `{row_action}` action.']
    }


def test_validate_delete_published_item(get_sync_items_env):
    get_sync_items_env['Items']['C2'].value = 'delete'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item status must be `draft` for the `delete` action.']
    }


def test_validate_create_published_item(get_sync_items_env):
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the `ID` must not be specified for the `create` action.']
    }


def test_validate_create_no_mpn(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['B2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `MPN` is required.']
    }


def test_validate_create_no_nome(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['D2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Name` is required for the `create` action.']
    }


def test_validate_create_no_description(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['E2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Description` is required for the `create` action.']
    }


def test_validate_create_strange_type(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['F2'].value = 'license'
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Type` must be one between `reservation` or `ppu`, not `license`.']
    }


def test_validate_wrong_precision_reservation(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['G2'].value = 'decimal'
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['for items of type `reservation` the `Precision` must be `integer`, not `decimal`.']
    }


def test_validate_wrong_precision_ppu(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['F2'].value = 'ppu'
    get_sync_items_env['Items']['G2'].value = 'decimal(12)'
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Precision` must be one between `integer`, `decimal(1)`, `decimal(2)`, '
            '`decimal(4)`, `decimal(8)`, not `decimal(12)`.']
    }


def test_validate_wrong_period_ppu(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['F2'].value = 'ppu'
    get_sync_items_env['Items']['I2'].value = 'yearly'
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['for items of type `ppu` the `Billing period` must be `monthly`, not `yearly`.']
    }


def test_validate_wrong_period_reservation(get_sync_items_env):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['I2'].value = 'century'
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env.save('./test.xlsx')
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Billing period` must be one between `onetime`, `monthly`, `yearly`, '
            '`2 years`, `3 years`, `4 years`, `5 years`, not `century`.']
    }


def test_create_item_exists_in_connect(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[mocked_items_response[0]]
    )
    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['Cannot create item: item with MPN `MPN-R-001` already exists with ID '
            '`PRD-276-377-545-0001`.']
    }


def test_create_item_connect_exception(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        status=500,
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['500 - Internal Server Error: unexpected error.']
    }


def test_create_item(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert errors == {}


def test_create_item_one_time(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['I2'].value = 'onetime'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert errors == {}


def test_create_item_yearly(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['J2'].value = '1 year'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert errors == {}


def test_create_item_1_to_1_yearly(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['I2'].value = 'yearly'
    get_sync_items_env['Items']['J2'].value = '1 year'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert errors == {}


def test_create_item_validate_commitment(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['I2'].value = 'yearly'
    get_sync_items_env['Items']['J2'].value = 'commitment'

    get_sync_items_env.save('./test.xlsx')

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the item `Commitment` must be one between `-`, `1 year`, `2 years`, `3 years`, '
            '`4 years`, `5 years`, not `commitment`.']
    }


def test_create_item_validate_commitment_ppu(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['F2'].value = 'ppu'
    get_sync_items_env['Items']['I2'].value = 'monthly'
    get_sync_items_env['Items']['J2'].value = '1 year'

    get_sync_items_env.save('./test.xlsx')

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the commitment `1 year` is invalid for `ppu` items.']
    }


def test_create_item_validate_commitment_onetime(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['F2'].value = 'reservation'
    get_sync_items_env['Items']['I2'].value = 'onetime'
    get_sync_items_env['Items']['J2'].value = '1 year'

    get_sync_items_env.save('./test.xlsx')

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['the commitment `1 year` is invalid for `onetime` items.']
    }


def test_create_item_validate_commitment_wrong_multiyear(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['F2'].value = 'reservation'
    get_sync_items_env['Items']['I2'].value = '2 years'
    get_sync_items_env['Items']['J2'].value = '3 years'

    get_sync_items_env.save('./test.xlsx')

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['for a billing period of `2 years` the commitment must be one between `-`, `4 years`, '
            ' not 3 years.']
    }


def test_create_item_validate_commitment_wrong_multiyear_vs_commitment(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['F2'].value = 'reservation'
    get_sync_items_env['Items']['I2'].value = '3 years'
    get_sync_items_env['Items']['J2'].value = '5 years'

    get_sync_items_env.save('./test.xlsx')

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['for a billing period of `3 years` the commitment must be `-`, not 5 years.']
    }


def test_update_item(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[mocked_items_response[0]],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert errors == {}


def test_delete_item(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'delete'
    get_sync_items_env['Items']['k2'].value = 'draft'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[mocked_items_response[0]],
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json={},
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_update_item_no_connect_item(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {
        2: ['Cannot update item: item with MPN `MPN-R-001` the item does not exist.']
    }


def test_update_item_no_item_connect(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'

    get_sync_items_env.save('./test.xlsx')

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {2: ['Cannot update item: item with MPN `MPN-R-001` the item does not exist.']}


def test_update_item_draft(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'

    item = mocked_items_response[0]
    item['status'] = 'draft'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[item],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert errors == {}


def test_update_item_draft_ppu(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'
    get_sync_items_env['Items']['F2'].value = 'ppu'

    item = mocked_items_response[0]
    item['status'] = 'draft'
    item['type'] = 'ppu'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[item],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json=mocked_items_response[0],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert errors == {}


def test_update_item_draft_connect_exception(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'update'

    item = mocked_items_response[0]
    item['status'] = 'draft'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[item],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        status=500,
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert errors == {2: ['500 - Internal Server Error: unexpected error.']}


def test_delete_item_not_exists(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'delete'
    get_sync_items_env['Items']['k2'].value = 'draft'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Cannot update item: item with MPN `MPN-R-001` the item does not exist.']
    }


def test_delete_item_connect_error(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'delete'
    get_sync_items_env['Items']['k2'].value = 'draft'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[mocked_items_response[0]],
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        status=500,
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 - Internal Server Error: unexpected error.']}


def test_create_item_custom_uom(
        get_sync_items_env,
        mocked_responses,
        mocked_items_response,
):
    get_sync_items_env['Items']['A2'].value = None
    get_sync_items_env['Items']['C2'].value = 'create'
    get_sync_items_env['Items']['H2'].value = 'unitary tests'

    get_sync_items_env.save('./test.xlsx')
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/settings/units',
        json={
            'id': '123'
        },
    )

    synchronizer = ItemSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Items')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert errors == {}
