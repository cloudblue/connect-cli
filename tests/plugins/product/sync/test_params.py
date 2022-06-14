from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.product.sync.params import ParamsSynchronizer
from connect.client import ConnectClient


def test_skipped(get_sync_params_env):

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/params_sync.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_skipped_fulfillment(get_sync_params_env):

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/params_sync.xlsx', 'Fulfillment Parameters')
    synchronizer.sync()

    assert stats['Fulfillment Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_validate_no_id(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['A2'] = None
    get_sync_params_env['Ordering Parameters']['B2'] = None
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['Parameter must have an id']}


def test_validate_invalid_id(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['B2'] = 'XKL#'
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Parameter ID must contain only letters, numbers and `_`, provided XKL#'],
    }


def test_validate_invalid_switch(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['F2'] = 'fulfillment'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Parameters of type ordering are only supported when processing Ordering Parameters. '
            'Has been provided fulfillment.'],
    }


def test_validate_invalid_action(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'
    get_sync_params_env['Ordering Parameters']['A2'] = None
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Verbose ID is required on update and delete actions.'],
    }


def test_validate_invalid_param_type(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['H2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Parameter type rocket is not one of the supported ones:email,address,checkbox,'
            'choice,domain,subdomain,url,dropdown,object,password,phone,text'],
    }


def test_validate_invalid_scope(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['G2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Only asset, tier1 and tier2 scopes are supported for Ordering Parameters'],
    }


def test_validate_invalid_scope_config(fs, get_sync_params_env):
    get_sync_params_env['Configuration Parameters']['C2'] = 'create'
    get_sync_params_env['Configuration Parameters']['G2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Configuration Parameters')
    synchronizer.sync()

    assert stats['Configuration Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Configuration Parameters']._row_errors == {
        2: ['Only item, item_marketplace, marketplace and product scopes are supported for '
            'Configuration Parameters'],
    }


def test_validate_invalid_required(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['I2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['Required must be either True or `-`']}


def test_validate_invalid_required2(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['J2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['Unique must be either True or `-`']}


def test_validate_invalid_required3(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['K2'] = 'rocket'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['Hidden must be either True or `-`']}


def test_validate_invalid_json(fs, get_sync_params_env):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['L2'] = 'nojson'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['JSON properties must have json format']}


def test_validate_delete(fs, get_sync_params_env, mocked_responses):
    get_sync_params_env['Ordering Parameters']['C2'] = 'delete'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters/PRM-276-377-545-0008',
        status=204,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_validate_delete_not_found(fs, get_sync_params_env, mocked_responses):
    get_sync_params_env['Ordering Parameters']['C2'] = 'delete'
    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters/PRM-276-377-545-0008',
        status=404,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_validate_update_invalid_switch(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'
    get_sync_params_env['Ordering Parameters']['H2'] = 'text'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {
        2: ['Switching parameter type is not supported'],
    }


def test_validate_update_invalid_switch_phase(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'

    response = mocked_ordering_params_response[0]
    response['phase'] = 'fulfillment'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['switching phase is not supported']}


def test_validate_update_invalid_switch_scope(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'

    response = mocked_ordering_params_response[0]
    response['scope'] = 'tier2'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['switching scope is not supported']}


def test_validate_update(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'update'

    response = mocked_ordering_params_response[0]

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters/PRM-276-377-545-0008',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_validate_create(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'

    response = mocked_ordering_params_response[0]

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_validate_create_connect_error(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Ordering Parameters']._row_errors == {2: ['500 Internal Server Error']}


def test_validate_create_no_constrains(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['L2'] = None

    response = mocked_ordering_params_response[0]

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=[],
    )

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_validate_skip_create_if_already_exists(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_validate_skip_create_but_update_if_differs_from_source(
    fs,
    get_sync_params_env,
    mocked_responses,
    mocked_ordering_params_response,
):
    get_sync_params_env['Ordering Parameters']['C2'] = 'create'
    get_sync_params_env['Ordering Parameters']['D2'] = 'Change on title test'

    get_sync_params_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ParamsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters',
        json=mocked_ordering_params_response[:1],
    )
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/parameters/PRM-276-377-545-0008',
        json=mocked_ordering_params_response[0],
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Ordering Parameters')
    synchronizer.sync()

    assert stats['Ordering Parameters'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
