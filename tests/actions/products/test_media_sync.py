from cnctcli.actions.products.media_sync import MediaSynchronizer
from cnct import ConnectClient


def test_no_action(get_sync_media_env):
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./tests/fixtures/media_sync.xlsx', 'Media')
    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 1
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {}


def test_validate_no_position(get_sync_media_env):
    get_sync_media_env['Media']['A2'] = None
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Position is required and must be an integer between 1 and 8']}


def test_validate_no_valid_id(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env['Media']['B2'] = 'wrong'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['ID does not seam to be valid.']}


def test_validate_no_image_file(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env['Media']['E2'] = None
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['Image file is required']}


def test_validate_wrong_action(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'XYZ'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Supported actions are `-`, `create`, `update` or `delete`. Provided XYZ']
    }


def test_validate_wrong_type(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'wrong'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Media can be either image or video type, provided wrong']
    }


def test_validate_wrong_file(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['E2'] = 'wrong.png'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Image file is not found, please check that file wrong.png exists in media folder']
    }


def test_validate_invalid_no_video_url(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = None
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Video URL location is required for video type']
    }


def test_validate_invalid_video_url(get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = 'http://goe.com/video.mov'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {
        2: ['Videos can be hosted on youtube or vimeo, please also ensure to provide https url. '
            'Invalid url provided is http://goe.com/video.mov']
    }


def test_delete(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=204,
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_404(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=404,
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 1
    assert errors == {}


def test_delete_500(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=500,
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['500 Internal Server Error']}


def test_update_image(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        json=mocked_media_response[0],
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 1
    assert deleted == 0
    assert errors == {}


def test_update_image_404(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=404,
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 0
    assert updated == 0
    assert deleted == 0
    assert errors == {2: ['404 Not Found']}


def test_create_video(get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = 'https://youtu.be/test'

    get_sync_media_env.save('./test.xlsx')

    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    synchronizer.open('./test.xlsx', 'Media')

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/media',
        json=mocked_media_response[0],
    )

    skipped, created, updated, deleted, errors = synchronizer.sync()

    assert skipped == 0
    assert created == 1
    assert updated == 0
    assert deleted == 0
    assert errors == {}
