from cnctcli.actions.products.utils import SheetNotFoundError
from click import ClickException
from cnctcli.actions.products.general_sync import GeneralSynchronizer
from cnct import ConnectClient
from openpyxl import load_workbook
from shutil import copy2

import pytest
import os


def test_sheet_not_found(fs):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    wb = load_workbook('./tests/fixtures/comparation_product.xlsx')
    wb.remove(wb['General Information'])
    wb.save('./test.xlsx')

    synchronizer = GeneralSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    with pytest.raises(ClickException) as e:
        synchronizer.open(
            './test.xlsx', 'General Information'
        )

    assert str(e.value) == 'File does not contain General Information to synchronize'


def test_no_product_id(fs):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    wb = load_workbook('./tests/fixtures/comparation_product.xlsx')
    ws = wb['General Information']
    ws['A5'].value = 'Modified'
    wb.save('./test.xlsx')

    synchronizer = GeneralSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )

    with pytest.raises(ClickException) as e:
        synchronizer.open(
            './test.xlsx', 'General Information'
        )

    assert str(e.value) == 'Input file has invalid format and could not read product id from it'


def test_open_product_not_found(fs, mocked_responses, mocked_product_response):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    synchronizer = GeneralSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json={},
        status=404,
    )
    with pytest.raises(ClickException) as e:
        synchronizer.open(
            './tests/fixtures/comparation_product.xlsx', 'General Information'
        )
    assert str(e.value) == "Product PRD-276-377-545 not found, create it first."


def test_open(fs, mocked_responses, mocked_product_response):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    synchronizer = GeneralSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        silent=True,
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545',
        json=mocked_product_response,
    )
    product_id = synchronizer.open(
        './tests/fixtures/comparation_product.xlsx', 'General Information'
    )

    assert product_id == 'PRD-276-377-545'
