import click
import pytest

from connect.client import ConnectClient
from connect.cli.plugins.shared.exceptions import SheetNotFoundError
from connect.cli.plugins.translation.sync import TranslationSynchronizer


localization_base = "https://localhost/public/v1/localization"


def get_client():
    return ConnectClient(
        api_key='ApiKey',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )


@pytest.mark.parametrize('sheet_name', ('General', 'Attributes'))
def test_sheet_not_found(fs, sheet_name, sample_translation_workbook):
    del sample_translation_workbook[sheet_name]
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)

    with pytest.raises(SheetNotFoundError) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx')

    assert str(e.value) == (
        "File must contain worksheets 'General' and 'Attributes' to synchronize, skipping"
    )


def test_invalid_file_open(fs):
    fs.create('fake.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xlsx')

    assert str(e.value).endswith("is not a valid xlsx file.")


def test_invalid_fileformat_open(fs):
    fs.create('fake.xxx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/fake.xxx')

    assert "openpyxl does not support .xxx file format" in str(e.value)


@pytest.mark.parametrize('row_to_invalidate', range(1, 10))
def test_general_sheet_validation(fs, row_to_invalidate, sample_translation_workbook):
    sample_translation_workbook['General'][f'A{row_to_invalidate}'].value = 'invalid'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx')

    assert str(e.value).startswith(f"A{row_to_invalidate} must be ")
    assert str(e.value).endswith(", but it is 'invalid'")


@pytest.mark.parametrize('col_idx', [1, 3, 4, 5, 6])
def test_attributes_sheet_validation(fs, col_idx, sample_translation_workbook):
    cell = sample_translation_workbook['Attributes'].cell(1, col_idx)
    cell.value = 'invalid'
    coordinate = cell.coordinate
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)

    with pytest.raises(click.ClickException) as e:
        synchronizer.open(f'{fs.root_path}/test.xlsx')

    assert str(e.value).startswith(f"Column '{coordinate}' must be ")
    assert str(e.value).endswith("but it is 'invalid'")


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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')
    with pytest.raises(click.ClickException) as e:
        synchronizer.sync(yes=False)

    assert "500 - Internal Server Error" in str(e.value)


def test_update_and_skip_all_attributes(
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
        json=mocked_translation_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 30, 'errors': 0,
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 0, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_update_attributes_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['Attributes']['C5'].value = 'update'
    sample_translation_workbook['Attributes']['C8'].value = 'update'
    sample_translation_workbook['Attributes']['C10'].value = 'update'
    sample_translation_workbook['Attributes']['C18'].value = 'update'
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
    mocked_responses.add(
        method='PUT',
        url=f'{localization_base}/translations/TRN-8100-3865-4869/attributes',
        status=500,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 25, 'errors': 5,
    }
    assert len(synchronizer.stats['Attributes']._row_errors) == 5


def test_update_wait_autotranslate_attributes(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['General']['B9'].value = 'Enabled'
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
    auto_processing_response = mocked_translation_response.copy()
    auto_processing_response['auto']['status'] = 'on'
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=auto_processing_response,
    )
    mocked_responses.add(
        method='PUT',
        url=f'{localization_base}/translations/TRN-8100-3865-4869/attributes',
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.DEFAULT_WAIT_SECONDS = 0.001
    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 29, 'errors': 0,
    }


@pytest.mark.parametrize('wait_response_auto,expected_error_msg', [
    (
        {'status': 'processing'},
        "Timeout waiting for pending translation tasks",
    ), (
        {'status': 'error', 'error_message': 'The auto-translation service failed'},
        "The auto-translation task failed with error: The auto-translation service failed",
    ), (
        {'status': 'unknown_status'},
        "Unknown auto-translation status: unknown_status",
    ),
])
def test_update_wait_autotranslate_fails(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
    wait_response_auto, expected_error_msg,
):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['General']['B9'].value = 'Enabled'
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
    auto_processing_response = mocked_translation_response.copy()
    auto_processing_response['auto'] = wait_response_auto
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-8100-3865-4869',
        json=auto_processing_response,
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.DEFAULT_WAIT_SECONDS = 0.001
    with pytest.raises(click.ClickException) as e:
        synchronizer.sync(yes=False)

    assert str(e.value) == expected_error_msg


def test_update(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook,
):
    sample_translation_workbook['Attributes']['C2'].value = 'update'
    sample_translation_workbook['Attributes']['C5'].value = 'update'
    sample_translation_workbook['Attributes']['C8'].value = 'update'
    sample_translation_workbook['Attributes']['C10'].value = 'update'
    sample_translation_workbook['Attributes']['C18'].value = 'update'
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
    mocked_responses.add(
        method='PUT',
        url=f'{localization_base}/translations/TRN-8100-3865-4869/attributes',
    )
    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 30, 'created': 0, 'updated': 5,
        'deleted': 0, 'skipped': 25, 'errors': 0,
    }


def test_create_asks_confirmation(
    fs, capsys, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    captured = capsys.readouterr()
    assert "A new translation will be created." in captured.out
    assert "Do you want to continue?" in captured.out


def test_abort_create(fs, mocked_responses, sample_translation_workbook, mocker):
    mocker.patch('click.termui.visible_prompt_func', return_value='n')
    sample_translation_workbook['General']['B1'].value = 'TRN-NON-EXISTENT'
    sample_translation_workbook.save(f'{fs.root_path}/test.xlsx')
    mocked_responses.add(
        method='GET',
        url=f'{localization_base}/translations/TRN-NON-EXISTENT',
        status=404,
    )

    client = get_client()
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.exceptions.Abort):
        synchronizer.sync(yes=False)


def test_create_always_yes(
    fs, capsys, mocked_responses, mocked_translation_response, sample_translation_workbook,
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=True)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
    captured = capsys.readouterr()
    assert "A new translation will be created." not in captured.out
    assert "Do you want to continue?" not in captured.out


def test_create_and_skip_all_attributes(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_create_fail_skip_attributes(
    fs, mocked_responses, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert synchronizer.stats['Attributes'].get_counts_as_dict() == {
        'processed': 0, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_change_locale_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_different_account_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-999-999', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


@pytest.mark.parametrize('ctx_instance_id', ['PRD-999-999-999', ''])
def test_change_context_causes_creation(
    fs, ctx_instance_id, mocked_responses, mocked_translation_response,
    sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_change_context_instance_causes_creation(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    synchronizer.sync(yes=False)

    assert synchronizer.stats['Translation'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_change_context_ambiguity_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync(yes=False)

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
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync(yes=False)

    assert str(e.value) == error_msg


def test_change_context_instance_not_exists_fail(
    fs, mocked_responses, mocked_translation_response, sample_translation_workbook, mocker,
):
    mocker.patch('click.termui.visible_prompt_func', return_value='y')
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
    synchronizer = TranslationSynchronizer(account_id='VA-063-000', client=client, silent=True)
    synchronizer.open(f'{fs.root_path}/test.xlsx')

    with pytest.raises(click.ClickException) as e:
        synchronizer.sync(yes=False)

    assert str(e.value) == "The Instance ID (PRD-INEXISTENT) doesn't exist"
