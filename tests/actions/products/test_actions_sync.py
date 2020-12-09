from cnctcli.actions.products.actions_sync import ActionsSynchronizer
from cnct import ConnectClient


def test_skipped(get_sync_actions_env):
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/actions_sync.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 1
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_validate_wrong_action(get_sync_actions_env):
    get_sync_actions_env['Actions']['C2'] = 'test'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Allowed action values are `-`, `create`, `update` or `delete`. test is not valid '
            'action.']
    }


def test_validate_no_verbose_id(get_sync_actions_env):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Verbose ID is required for update action.']}


def test_validate_wrong_id(get_sync_actions_env):
    get_sync_actions_env['Actions']['B2'] = 'wrong id'
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Actions ID must contain only letters, numbers and `_`, provided wrong id']
    }


def test_validate_wrong_scope(get_sync_actions_env):
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env['Actions']['G2'] = 'tier3'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Action scope must be one of `asset`, `tier1` or `tier2`. Provided tier3']
    }


def test_delete(get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=204,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_404(get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=404,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_500(get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}

def test_update(get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['C2'] = 'update'

    response = mocked_actions_response[0]

    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        json=response,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert deleted == 0
    assert errors == {}


def test_update_500(get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['C2'] = 'update'

    response = mocked_actions_response[0]

    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}


def test_create(get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'

    response = mocked_actions_response[0]

    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        json=response,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_create_500(get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'

    response = mocked_actions_response[0]

    get_sync_actions_env.save('./test.xlsx')

    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Actions')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}
