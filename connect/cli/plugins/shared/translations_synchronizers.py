from click import ClickException

from connect.cli.plugins.shared.translation_sync import TranslationsSynchronizer
from connect.cli.plugins.shared.translation_attr_sync import TranslationAttributesSynchronizer
from connect.cli.plugins.shared.utils import (
    get_translation_attributes_sheets,
    wait_for_autotranslation,
)
from connect.cli.plugins.shared.exceptions import SheetNotFoundError


def translations_sync(client, progress, input_file, stats, save):
    synchronizer = TranslationsSynchronizer(client, progress, stats)
    synchronizer.open(input_file, 'Translations')
    synchronizer.sync()
    if save:
        synchronizer.save(input_file)
    return synchronizer


def translation_attributes_sync(worksheet, translation, client, progress, input_file, stats, save, is_clone):
    synchronizer = TranslationAttributesSynchronizer(client, progress, stats)
    synchronizer.open(input_file, worksheet)
    synchronizer.sync(translation, is_clone)
    if save:
        synchronizer.save(input_file)


def sync_product_translations(client, progress, input_file, stats, save=True, is_clone=False):
    translations_autotranslating = []
    try:
        synchronizer = translations_sync(client, progress, input_file, stats, save)
        translations_autotranslating = synchronizer.translations_autotranslating
        new_translations = synchronizer.new_translations
    except SheetNotFoundError as e:
        raise ClickException(str(e))

    new_translations.insert(0, None)
    iter_translation = iter(new_translations)
    for sheetname in get_translation_attributes_sheets(input_file):
        translation = sheetname.split()[1][1:-1]
        if is_clone:
            translation = next(iter_translation)
        if translation in translations_autotranslating:
            wait_for_autotranslation(client, progress, translation)
        translation_attributes_sync(
            sheetname, translation, client,
            progress, input_file, stats, save, is_clone,
        )
