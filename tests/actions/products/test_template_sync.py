from cnctcli.actions.products.templates_sync import TemplatesSynchronizer
from cnct import ConnectClient


def test_no_action(get_sync_templates_env):
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/templates_sync.xlsx', 'Templates')
    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 1
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_invalid_scope(get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['D2'] = 'noscope'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Valid scopes are `asset`, `tier1` or `tier2`, not noscope']}


def test_invalid_type(get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['E2'] = 'invalid'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Valid template types are `pending`, `fulfillment` or inquiring. '
                          'Provided invalid.']}


def test_invalid_tier_type(get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['D2'] = 'tier1'
    get_sync_templates_env['Templates']['E2'] = 'inquire'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Tier templates must be fulfillment type only']}


def test_invalid_no_title(get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['B2'] = None
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Title and Content are required']}


def test_invalid_id(get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env['Templates']['A2'] = 'XTL-1234'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Update operation requires template id']}


def test_create_template(get_sync_templates_env, mocked_templates_response, mocked_responses):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['A2'] = None

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates',
        json=mocked_templates_response[0],
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_create_template_error(get_sync_templates_env, mocked_templates_response, mocked_responses):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['A2'] = None

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}


def test_update_template_not_exists(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=404,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Cannot update template TL-551-876-782 since does not exist in the product.Create it '
            'instead']
    }


def test_delete_template_not_exists(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=404,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_template_500(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}


def test_delete_template(get_sync_templates_env, mocked_templates_response, mocked_responses):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=mocked_templates_response[0],
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=204,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_update_template_switch_type(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    response = mocked_templates_response[0]
    response['type'] = 'tier1'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=response,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Switching scope or type is not supported. Original scope asset, requested scope '
            'asset. Original type tier1, requested type fulfillment']
    }


def test_update_template(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=mocked_templates_response[0],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=mocked_templates_response[0],
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert deleted == 0
    assert errors == {}


def test_update_template_exception(
        get_sync_templates_env,
        mocked_templates_response,
        mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env.save('./test.xlsx')

    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=mocked_templates_response[0],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=500,
    )

    synchronizer.open('./test.xlsx', 'Templates')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}
