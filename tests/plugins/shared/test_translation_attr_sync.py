import click
import pytest

from connect.client import ConnectClient
from connect.cli.plugins.shared.exceptions import SheetNotFoundError
from connect.cli.plugins.shared.translation_attr_sync import TranslationAttributesSynchronizer


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )


def test_sheet_not_found(fs, sample_translation_workbook):
    del sample_translation_workbook['Attributes']
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)

    with pytest.raises(SheetNotFoundError) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx', 'Attributes')

    assert str(e.value) == (
        "File does not contain worksheet 'Attributes' to synchronize, skipping"
    )


def test_invalid_file_open(fs):
    fs.create('fake.xlsx')
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xlsx', 'Attributes')

    assert str(e.value).endswith("is not a valid xlsx file.")


def test_invalid_fileformat_open(fs):
    fs.create('fake.xxx')
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xxx', 'Attributes')

    assert "openpyxl does not support .xxx file format" in str(e.value)


@pytest.mark.parametrize('col_idx', [1, 3, 4, 5, 6])
def test_sheet_validation(fs, col_idx, sample_translation_workbook):
    cell = sample_translation_workbook['Attributes'].cell(1, col_idx)
    cell.value = 'invalid'
    coordinate = cell.coordinate
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx', 'Attributes')

    assert str(e.value).startswith(f"Column '{coordinate}' must be ")
    assert str(e.value).endswith("but it is 'invalid'")


def test_update_fail(fs, mocked_responses, sample_translation_workbook):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['Attributes']['C5'].value = 'update'
    sample_translation_workbook['Attributes']['C8'].value = 'update'
    sample_translation_workbook['Attributes']['C10'].value = 'update'
    sample_translation_workbook['Attributes']['C18'].value = 'update'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/attributes',
        status=500,
    )
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Attributes')

    synchronizer.sync(translation_id='TRN-8100-3865-4869')

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 25, 'errors': 5,
    }
    assert len(synchronizer._mstats._row_errors) == 5


def test_update_ok(fs, mocked_responses, sample_translation_workbook):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['Attributes']['C5'].value = 'update'
    sample_translation_workbook['Attributes']['C8'].value = 'update'
    sample_translation_workbook['Attributes']['C10'].value = 'update'
    sample_translation_workbook['Attributes']['C18'].value = 'update'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/localization/translations/TRN-8100-3865-4869/attributes',
        status=200,
    )
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Attributes')

    synchronizer.sync(translation_id='TRN-8100-3865-4869')

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 5,
        'deleted': 0, 'skipped': 25, 'errors': 0,
    }


def test_nothing_to_update(fs, sample_translation_workbook):
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationAttributesSynchronizer(client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Attributes')

    synchronizer.sync(translation_id='TRN-8100-3865-4869')

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 30, 'errors': 0,
    }
