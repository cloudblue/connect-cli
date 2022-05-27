from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.product.sync.translations import TranslationsSynchronizer
from connect.client import ConnectClient


def test_skipped(fs, get_sync_translations_env):
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 2, 'errors': 0,
    }


def test_validate_invalid_action(fs, get_sync_translations_env):
    get_sync_translations_env['Translations']['B3'] = 'invalid'
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 1,
    }
    assert stats['Translations']._row_errors == {
        3: ['Action must be `-`, `delete`, `update` or `create`. Provided invalid'],
    }


def test_validate_cant_delete_primary(fs, get_sync_translations_env):
    get_sync_translations_env['Translations']['B2'] = 'delete'
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 1,
    }
    assert stats['Translations']._row_errors == {
        2: ['Can\'t delete the primary translation'],
    }


def test_validate_translation_id(fs, get_sync_translations_env):
    get_sync_translations_env['Translations']['A3'] = None
    get_sync_translations_env['Translations']['B3'] = 'update'
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 1,
    }
    assert stats['Translations']._row_errors == {
        3: ['Translation ID is required to update or delete a translation'],
    }


def test_validate_autotranslation(fs, get_sync_translations_env):
    get_sync_translations_env['Translations']['B2'] = 'update'
    get_sync_translations_env['Translations']['I2'] = 'invalid'
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 1,
    }
    assert stats['Translations']._row_errors == {
        2: ['Autotranslation must be `Enabled` or `Disabled`. Provided invalid'],
    }


def test_validate_locale(fs, get_sync_translations_env):
    get_sync_translations_env['Translations']['B3'] = 'create'
    get_sync_translations_env['Translations']['G3'] = None
    get_sync_translations_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = TranslationsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Translations')
    synchronizer.sync()

    assert stats['Translations'].get_counts_as_dict() == {
        'processed': 2, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 1,
    }
    assert stats['Translations']._row_errors == {
        3: ['Locale is required to create a translation'],
    }
