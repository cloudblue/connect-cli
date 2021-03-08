from cnctcli.actions.customers_syncronizer import CustomerSynchronizer
from cnct import ConnectClient


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False
    )


def test_sync_all_skip(fs, customers_workbook):
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert skipped == 2
    assert created == 0
    assert updated == 0
    assert len(errors) == 0


def test_bad_action(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'wrong'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Action wrong is not supported']}


def test_bad_account(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook['Customers']['H2'] = 'robot'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Customer type must be customer or reseller, not robot']}


def test_empty_address(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook['Customers']['K2'] = ''
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Address line 1, city, state and zip are mandatory']}


def test_create_existing(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Create action must not have account id, is set to TA-7374-0753-1907']}


def test_create_customer_no_parent(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook['Customers']['H2'] = 'customer'
    customers_workbook['Customers']['A2'] = None
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Customers requires a parent account']}


def test_update_customer_no_id(fs, customers_workbook):
    customers_workbook['Customers']['D2'] = 'update'
    customers_workbook['Customers']['A2'] = 'KA-'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Update operation requires account ID to be set']}


def test_update_customer_no_account_connect(fs, customers_workbook, mocked_responses):
    customers_workbook['Customers']['D2'] = 'update'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/tier/accounts/TA-7374-0753-1907',
        status=404
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {2: ['Account with id TA-7374-0753-1907 does not exist']}


def test_create_account_connect(fs, customers_workbook, mocked_responses, mocked_reseller):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook['Customers']['A2'] = None
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/tier/accounts',
        json=mocked_reseller
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert created == 1


def test_create_account_connect_uuid(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D2'] = 'create'
    customers_workbook['Customers']['A2'] = None
    customers_workbook['Customers']['C2'] = None
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/tier/accounts',
        json=mocked_reseller
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert created == 1


def test_create_account_connect_parent_id(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/tier/accounts',
        json=mocked_reseller
    )
    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts/{mocked_reseller["id"]}',
        json=mocked_reseller
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert created == 1


def test_create_account_connect_parent_id_not_found(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts/{mocked_reseller["id"]}',
        status=404
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {3: [f'Parent with id {mocked_reseller["id"]} does not exist']}


def test_create_account_connect_parent_external_id(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_id'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_id,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[mocked_reseller],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_id,{mocked_reseller["id"]})&limit=1&offset=0',
        json=[mocked_reseller],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/tier/accounts',
        json=mocked_reseller
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert created == 1


def test_create_account_connect_parent_external_id_not_found(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_id'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_id,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {3: ['Parent with external_id TA-7374-0753-1907 not found']}


def test_create_account_connect_parent_external_id_more_than_one(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_id'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_id,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-2/2',
        },
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {3: ['More than one Parent with external_id TA-7374-0753-1907']}


def test_create_account_connect_parent_external_uid(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_uid'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_uid,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[mocked_reseller],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_uid,{mocked_reseller["id"]})&limit=1&offset=0',
        json=[mocked_reseller],
        headers={
            'Content-Range': 'items 0-1/1',
        },
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/tier/accounts',
        json=mocked_reseller
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert created == 1


def test_create_account_connect_parent_external_uid_not_found(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_uid'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_uid,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-0/0',
        },
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {3: ['Parent with external_uid TA-7374-0753-1907 not found']}


def test_create_account_connect_parent_external_uid_more_than_one(
        fs,
        customers_workbook,
        mocked_responses,
        mocked_reseller
):
    customers_workbook['Customers']['D3'] = 'create'
    customers_workbook['Customers']['A3'] = None
    customers_workbook['Customers']['C3'] = None
    customers_workbook['Customers']['F3'] = 'external_uid'
    customers_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()

    mocked_responses.add(
        method='GET',
        url=f'https://localhost/public/v1/tier/accounts?eq(external_uid,{mocked_reseller["id"]})&limit=0&offset=0',
        json=[],
        headers={
            'Content-Range': 'items 0-2/2',
        },
    )
    synchronizer = CustomerSynchronizer(
        account_id='VA-123',
        client=client,
        silent=True
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Customers')
    skipped, created, updated, errors = synchronizer.sync()
    assert errors == {3: ['More than one Parent with external_uid TA-7374-0753-1907']}