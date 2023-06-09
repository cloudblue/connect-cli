import pytest
from click import ClickException

from connect.cli.plugins.shared.exceptions import SheetNotFoundError
from connect.cli.plugins.shared.translations_synchronizers import (
    sync_product_translations,
    translation_attributes_sync,
    translations_sync,
)


@pytest.mark.parametrize('save', (True, False))
def test_translations_sync(mocker, save):
    synchronizer = mocker.MagicMock()
    mocked_sync = mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.TranslationsSynchronizer',
        return_value=synchronizer,
    )

    progress = mocker.MagicMock()
    client = mocker.MagicMock()
    input_file = mocker.MagicMock()
    stats = mocker.MagicMock()

    translations_sync(client, progress, input_file, stats, save)

    mocked_sync.assert_called_once_with(client, progress, stats)
    synchronizer.open.assert_called_once_with(input_file, 'Translations')
    synchronizer.sync.assert_called_once()
    if save:
        synchronizer.save.assert_called_once_with(input_file)
    else:
        synchronizer.save.assert_not_called()


@pytest.mark.parametrize('save', (True, False))
def test_translation_attributes_sync(mocker, save):
    synchronizer = mocker.MagicMock()
    mocked_sync = mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.TranslationAttributesSynchronizer',
        return_value=synchronizer,
    )

    progress = mocker.MagicMock()
    client = mocker.MagicMock()
    input_file = mocker.MagicMock()
    stats = mocker.MagicMock()
    worksheet = mocker.MagicMock()
    translation = mocker.MagicMock()
    is_clone = mocker.MagicMock()

    translation_attributes_sync(
        worksheet,
        translation,
        client,
        progress,
        input_file,
        stats,
        save,
        is_clone,
    )

    mocked_sync.assert_called_once_with(client, progress, stats)
    synchronizer.open.assert_called_once_with(input_file, worksheet)
    synchronizer.sync.assert_called_once_with(translation, is_clone)
    if save:
        synchronizer.save.assert_called_once_with(input_file)
    else:
        synchronizer.save.assert_not_called()


@pytest.mark.parametrize('is_clone', (True, False))
def test_sync_product_translations(mocker, is_clone):
    synchronizer = mocker.MagicMock()
    synchronizer.translations_autotranslating = []
    synchronizer.new_translations = []
    mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.translations_sync',
        return_value=synchronizer,
    )

    mocked_attr_sync = mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.translation_attributes_sync',
    )

    mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.get_translation_attributes_sheets',
        return_value=['IT-IT (TRN-000)'],
    )

    client = mocker.MagicMock()
    progress = mocker.MagicMock()
    input_file = mocker.MagicMock()
    stats = mocker.MagicMock()

    sync_product_translations(client, progress, input_file, stats, is_clone=is_clone)

    mocked_attr_sync.assert_called_once_with(
        'IT-IT (TRN-000)',
        'TRN-000' if not is_clone else None,
        client,
        progress,
        input_file,
        stats,
        True,
        is_clone,
    )


def test_sync_product_translations_sheet_not_found(mocker):
    mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.translations_sync',
        side_effect=SheetNotFoundError('error'),
    )

    with pytest.raises(ClickException) as cv:
        sync_product_translations(
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
            mocker.MagicMock(),
        )

    assert str(cv.value) == 'error'


def test_sync_product_translations_wait_autotranslation(mocker):
    synchronizer = mocker.MagicMock()
    synchronizer.translations_autotranslating = ['TRN-000']
    synchronizer.new_translations = []
    mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.translations_sync',
        return_value=synchronizer,
    )

    mocked_attr_sync = mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.translation_attributes_sync',
    )

    mocked_wait_autotrans = mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.wait_for_autotranslation',
    )

    mocker.patch(
        'connect.cli.plugins.shared.translations_synchronizers.get_translation_attributes_sheets',
        return_value=['IT-IT (TRN-000)'],
    )

    client = mocker.MagicMock()
    progress = mocker.MagicMock()
    input_file = mocker.MagicMock()
    stats = mocker.MagicMock()

    sync_product_translations(client, progress, input_file, stats)

    mocked_attr_sync.assert_called_once_with(
        'IT-IT (TRN-000)',
        'TRN-000',
        client,
        progress,
        input_file,
        stats,
        True,
        False,
    )

    mocked_wait_autotrans.assert_called_once_with(
        client,
        progress,
        'TRN-000',
    )
