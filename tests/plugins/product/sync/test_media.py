import pytest

from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.product.sync.media import MediaSynchronizer
from connect.client import ConnectClient


def test_no_action(get_sync_media_env):
    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/media_sync.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_validate_no_position(fs, get_sync_media_env):
    get_sync_media_env['Media']['A2'] = None
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Position is required and must be an integer between 1 and 8'],
    }


def test_validate_no_valid_id(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env['Media']['B2'] = 'wrong'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['ID does not seam to be valid.'],
    }


def test_validate_no_image_file(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env['Media']['E2'] = None
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {2: ['Image file is required']}


def test_validate_wrong_action(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'XYZ'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Supported actions are `-`, `create`, `update` or `delete`. Provided XYZ'],
    }


def test_validate_wrong_type(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'wrong'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Media can be either image or video type, provided wrong'],
    }


def test_validate_wrong_file(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['E2'] = 'wrong.png'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Image file is not found, please check that file wrong.png exists in media folder'],
    }


def test_validate_invalid_no_video_url(fs, get_sync_media_env):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = None
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Video URL location is required for video type'],
    }


@pytest.mark.parametrize('video_domain', ('goe.com', 'vimeo.comyoutube.com'))
def test_validate_invalid_video_url(fs, get_sync_media_env, video_domain):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = f'http://{video_domain}/video.mov'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {
        2: ['Videos can be hosted on youtube or vimeo, please also ensure to provide https url. '
            f'Invalid url provided is http://{video_domain}/video.mov'],
    }


def test_delete(fs, get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=204,
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_delete_404(fs, get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=404,
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_delete_500(fs, get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'delete'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=500,
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {2: ['500 Internal Server Error']}


def test_update_image(fs, get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        json=mocked_media_response[0],
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_update_image_404(fs, get_sync_media_env, mocked_responses, mocked_media_response):
    get_sync_media_env['Media']['C2'] = 'update'
    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/media/PRDM-276-377-545-67072',
        status=404,
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Media']._row_errors == {2: ['404 Not Found']}


@pytest.mark.parametrize('domain', ('youtu.be', 'vimeo.com', 'youtube.com'))
def test_create_video(fs, get_sync_media_env, mocked_responses, mocked_media_response, domain):
    get_sync_media_env['Media']['C2'] = 'create'
    get_sync_media_env['Media']['D2'] = 'video'
    get_sync_media_env['Media']['E2'] = 'image.png'
    get_sync_media_env['Media']['F2'] = f'https://{domain}/test'

    get_sync_media_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = MediaSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Media')

    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/media',
        json=mocked_media_response[0],
    )
    synchronizer.sync()

    assert stats['Media'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
