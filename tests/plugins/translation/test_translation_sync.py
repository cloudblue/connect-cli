import click
import pytest
from connect.client import ConnectClient

from connect.cli.plugins.shared.exceptions import SheetNotFoundError
from connect.cli.plugins.translation.translation_sync import TranslationSynchronizer


localization_base = "https://localhost/public/v1/localization"


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )


def test_sheet_not_found(fs, sample_translation_workbook):
    del sample_translation_workbook['General']
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)

    with pytest.raises(SheetNotFoundError) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx')

    assert str(e.value) == (
        "File does not contain worksheet 'General' to synchronize, skipping"
    )


def test_invalid_file_open(fs):
    fs.create('fake.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xlsx')

    assert str(e.value).endswith("is not a valid xlsx file.")


def test_invalid_fileformat_open(fs):
    fs.create('fake.xxx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xxx')

    assert "openpyxl does not support .xxx file format" in str(e.value)


@pytest.mark.parametrize('row_to_invalidate', range(1, 10))
def test_sheet_validation(fs, row_to_invalidate, sample_translation_workbook):
    sample_translation_workbook['General'][f'A{row_to_invalidate}'].value = 'invalid'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx')

    assert str(e.value).startswith(f"A{row_to_invalidate} must be ")
    assert str(e.value).endswith(", but it is 'invalid'")


def test_get_translation_error_500(
    fs, mocked_responses, sample_translation_workbook,
):
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        status=500,
    )

    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')
    with pytest.raises(click.ClickException) as e:
        synchronizer.sync()

    assert "500 - Internal Server Error" in str(e.value)


def test_update_ok(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook['General']['B8'].value = 'new description'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )

    mocked_responses.add(
        method='PUT',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_update_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )

    mocked_responses.add(
        method='PUT',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        status=500,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }


def test_create_asks_confirmation(
    fs, capsys, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B1'].value = 'TRN-NON-EXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-NON-EXISTENT',
        status=404,
    )

    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    captured = capsys.readouterr()
    assert "A new translation will be created." in captured.out
    assert "Do you want to continue?" in captured.out


def test_abort_create(fs, mocked_responses, sample_translation_workbook, mocker):
    mocker.patch('builtins.input', lambda *args: 'n')
    sample_translation_workbook['General']['B1'].value = 'TRN-NON-EXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-NON-EXISTENT',
        status=404,
    )

    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.exceptions.Abort):
        synchronizer.sync()


def test_create_always_yes(
    always_yes_console, fs, capsys, mocked_responses,
    mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook['General']['B1'].value = 'TRN-NON-EXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-NON-EXISTENT',
        status=404,
    )

    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')
    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    captured = capsys.readouterr()
    assert "A new translation will be created." not in captured.out
    assert "Do you want to continue?" not in captured.out


def test_create_fail(
    fs, mocked_responses, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B1'].value = 'TRN-NON-EXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-NON-EXISTENT',
        status=404,
    )
    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        status=500,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }


def test_change_locale_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B4'].value = 'DE'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_different_account_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )

    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-999-999', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


@pytest.mark.parametrize('ctx_instance_id', ['PRD-999-999-999', ''])
def test_change_context_causes_creation(
    fs, ctx_instance_id, mocked_responses, mocked_translation_response,
    sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B5'].value = 'LCX-9999-9999-9999'
    sample_translation_workbook['General']['B6'].value = ctx_instance_id
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/contexts/LCX-9999-9999-9999',
        json={
            'id': 'LCX-9999-9999-9999',
            'instance_id': 'PRD-999-999-999', 'name': 'another product',
        },
    )
    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_change_context_instance_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B5'].value = ''
    sample_translation_workbook['General']['B6'].value = 'PRD-999-999-999'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/contexts?eq(instance_id,PRD-999-999-999)&limit=1&offset=0',
        headers={
            'Content-Range': 'items 0-0/1',
        },
        json=[{
            'id': 'LCX-9999-9999-9999',
            'instance_id': 'PRD-999-999-999', 'name': 'another product',
        }],
    )
    mocked_responses.add(
        method='POST',
        url=f'{localization_base}/translations',
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync()

    assert synchronizer._mstats.get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_change_context_ambiguity_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B5'].value = 'LCX-9999-9999-9999'
    sample_translation_workbook['General']['B6'].value = 'PRD-DIFFERENT-PRODUCT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/contexts/LCX-9999-9999-9999',
        json={
            'id': 'LCX-9999-9999-9999',
            'instance_id': 'PRD-999-999-999', 'name': 'another product',
        },
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync()

    assert str(e.value) == (
        "The Instance ID (PRD-DIFFERENT-PRODUCT) doesn't correspond "
        "to the Context ID (LCX-9999-9999-9999)"
    )


@pytest.mark.parametrize('status,error_msg', [
    (404, "The Context ID (LCX-TRIGGER-ERROR) doesn't exist"),
    (500, "500 - Internal Server Error: unexpected error."),
])
def test_change_context_fail(
    fs, status, error_msg, mocked_responses, mocked_translation_response,
    sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B5'].value = 'LCX-TRIGGER-ERROR'
    sample_translation_workbook['General']['B6'].value = ''
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/contexts/LCX-TRIGGER-ERROR',
        status=status,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync()

    assert str(e.value) == error_msg


def test_change_context_instance_not_exists_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('builtins.input', lambda *args: 'y')
    sample_translation_workbook['General']['B5'].value = ''
    sample_translation_workbook['General']['B6'].value = 'PRD-INEXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=mocked_translation_response,
    )
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/contexts?eq(instance_id,PRD-INEXISTENT)&limit=1&offset=0',
        headers={
            'Content-Range': 'items 0-0/0',
        },
        json=[],
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync()

    assert str(e.value) == "The Instance ID (PRD-INEXISTENT) doesn't exist"
