from connect.client import ConnectClient
from responses import matchers

from connect.cli.plugins.product.sync.templates import TemplatesSynchronizer
from connect.cli.plugins.shared.sync_stats import SynchronizerStats


def test_no_action(mocker, get_sync_templates_env):
    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/templates_sync.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 1,
        'errors': 0,
    }


def test_invalid_scope(mocker, fs, get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['D2'] = 'noscope'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {
        2: ['Valid scopes are `asset`, `tier1` or `tier2`, not noscope'],
    }


def test_invalid_type(mocker, fs, get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['E2'] = 'invalid'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {
        2: [
            'Valid template types are `pending`, `fulfillment` or `inquiring`. '
            'Provided invalid.',
        ],
    }


def test_invalid_no_title(mocker, fs, get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['B2'] = None
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {2: ['Title and Content are required']}


def test_invalid_id(mocker, fs, get_sync_templates_env):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env['Templates']['A2'] = 'XTL-1234'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {2: ['Update operation requires template id']}


def test_create_template(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['A2'] = None

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
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
        url='https://localhost/public/v1/products/PRD-276-377-545/templates',
        json=mocked_templates_response[0],
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 1,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }


def test_create_template_error(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['A2'] = None

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
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
        url='https://localhost/public/v1/products/PRD-276-377-545/templates',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {2: ['500 Internal Server Error']}


def test_create_template_for_tier_scope_ignore_type(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'create'
    get_sync_templates_env['Templates']['A2'] = None
    get_sync_templates_env['Templates']['D2'] = 'tier1'
    get_sync_templates_env['Templates']['E2'] = 'fulfillment'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
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
        url='https://localhost/public/v1/products/PRD-276-377-545/templates',
        match=[
            matchers.json_params_matcher(
                {
                    'name': 'Template 1',
                    'scope': 'tier1',
                    'body': (
                        '# Template 1\n\n'
                        'This is **template 1** with the following parameters:\n\n'
                        '1. t0_o_email = {{ t0_o_email }}\n'
                        '2. t0_f_password = {{ t0_f_password }}\n'
                        '3. t0_f_text = {{ t0_f_text }}\n\n'
                        'Have a nice day!'
                    ),
                },
            ),
        ],
        json=mocked_templates_response[0],
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 1,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }


def test_update_template_not_exists(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=404,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {
        2: [
            'Cannot update template TL-551-876-782 since does not exist in the product. Create it '
            'instead',
        ],
    }


def test_delete_template_not_exists(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=404,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 1,
        'skipped': 0,
        'errors': 0,
    }


def test_delete_template_500(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {2: ['500 Internal Server Error']}


def test_delete_template(mocker, fs, get_sync_templates_env, mocked_responses):
    get_sync_templates_env['Templates']['C2'] = 'delete'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        status=204,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 1,
        'skipped': 0,
        'errors': 0,
    }


def test_update_template_switch_type(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    response = mocked_templates_response[0]
    response['type'] = 'tier1'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {
        2: [
            'Switching scope or type is not supported. Original scope asset, requested scope '
            'asset. Original type tier1, requested type fulfillment',
        ],
    }


def test_update_template(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
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

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }


def test_update_template_exception(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
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

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': 1,
    }
    assert stats['Templates']._row_errors == {2: ['500 Internal Server Error']}


def test_update_template_for_tier_scope_ignore_type(
    mocker,
    fs,
    get_sync_templates_env,
    mocked_templates_response,
    mocked_responses,
):
    get_sync_templates_env['Templates']['C2'] = 'update'
    get_sync_templates_env['Templates']['D2'] = 'tier1'
    get_sync_templates_env['Templates']['E2'] = 'fulfillment'

    get_sync_templates_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TemplatesSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        json=mocked_templates_response[1],
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/templates/TL-551-876-782',
        match=[
            matchers.json_params_matcher(
                {
                    'name': 'Template 1',
                    'scope': 'tier1',
                    'body': (
                        '# Template 1\n\n'
                        'This is **template 1** with the following parameters:\n\n'
                        '1. t0_o_email = {{ t0_o_email }}\n'
                        '2. t0_f_password = {{ t0_f_password }}\n'
                        '3. t0_f_text = {{ t0_f_text }}\n\n'
                        'Have a nice day!'
                    ),
                },
            ),
        ],
        json=mocked_templates_response[1],
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Templates')
    synchronizer.sync()

    assert stats['Templates'].get_counts_as_dict() == {
        'processed': 1,
        'created': 0,
        'updated': 1,
        'deleted': 0,
        'skipped': 0,
        'errors': 0,
    }
