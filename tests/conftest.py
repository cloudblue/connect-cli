import json

import pytest

import responses

import os
from shutil import copy2

from tests.data import CONFIG_DATA
from openpyxl import load_workbook


@pytest.fixture(scope='function')
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )


@pytest.fixture(scope='function')
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope='function')
def mocked_product_response(fs):
    fs.add_real_file('./tests/fixtures/product_response.json')
    with open('./tests/fixtures/product_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_categories_response(fs):
    fs.add_real_file('./tests/fixtures/categories_response.json')
    with open('./tests/fixtures/categories_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_media_response(fs):
    fs.add_real_file('./tests/fixtures/media_response.json')
    with open('./tests/fixtures/media_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_templates_response(fs):
    fs.add_real_file('./tests/fixtures/templates_response.json')
    with open('./tests/fixtures/templates_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_items_response(fs):
    fs.add_real_file('./tests/fixtures/items_response.json')
    with open('./tests/fixtures/items_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_ordering_params_response(fs):
    fs.add_real_file('./tests/fixtures/ordering_parameters_response.json')
    with open('./tests/fixtures/ordering_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_fulfillment_params_response(fs):
    fs.add_real_file('./tests/fixtures/fulfillment_parameters_response.json')
    with open('./tests/fixtures/fulfillment_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_configuration_params_response(fs):
    fs.add_real_file('./tests/fixtures/configuration_parameters_response.json')
    with open('./tests/fixtures/configuration_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_actions_response(fs):
    fs.add_real_file('./tests/fixtures/actions_response.json')
    with open('./tests/fixtures/actions_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_configurations_response(fs):
    fs.add_real_file('./tests/fixtures/configurations_response.json')
    with open('./tests/fixtures/configurations_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def sample_product_workbook(fs):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    return load_workbook('./tests/fixtures/comparation_product.xlsx')


@pytest.fixture(scope='function')
def get_sync_items_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/items_sync.xlsx')
    fs.add_real_file('./tests/fixtures/units_response.json')
    fs.add_real_file('./tests/fixtures/product_response.json')
    with open('./tests/fixtures/units_response.json') as response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/settings/units',
            json=json.load(response)
        )
        with open('./tests/fixtures/product_response.json') as prod_response:
            mocked_responses.add(
                method='GET',
                url='https://localhost/public/v1/products/PRD-276-377-545',
                json=json.load(prod_response)
            )

            return load_workbook('./tests/fixtures/items_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_actions_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/actions_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response_modifications.json')
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/actions_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_capabilities_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/capabilities_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response_modifications.json')
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/capabilities_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_params_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/params_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response_modifications.json')
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/params_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_config_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/configuration_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response_modifications.json')
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/configuration_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_templates_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/templates_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response.json')
    with open('./tests/fixtures/product_response.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/templates_sync.xlsx')


@pytest.fixture(scope='function')
def get_general_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/comparation_product.xlsx')
    fs.add_real_file('./tests/fixtures/categories_response.json')
    fs.add_real_file('./tests/fixtures/product_response.json')
    fs.add_real_file('./tests/fixtures/image.png')
    os.mkdir('./media')
    copy2('./tests/fixtures/image.png', './media/PRD-276-377-545.png')
    with open('./tests/fixtures/categories_response.json') as cat_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/categories',
            json=json.load(cat_response),
        )
        with open('./tests/fixtures/product_response.json') as prod_response:
            mocked_responses.add(
                method='GET',
                url='https://localhost/public/v1/products/PRD-276-377-545',
                json=json.load(prod_response)
            )

        return load_workbook('./tests/fixtures/comparation_product.xlsx')


@pytest.fixture(scope='function')
def get_sync_media_env(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/media_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response.json')
    fs.add_real_file('./tests/fixtures/image.png')
    os.mkdir('./media')
    copy2('./tests/fixtures/image.png', './media/image.png')
    with open('./tests/fixtures/product_response.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response)
        )

        return load_workbook('./tests/fixtures/media_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_capabilities_env_ppu_enabled(fs, mocked_responses):
    fs.add_real_file('./tests/fixtures/capabilities_sync.xlsx')
    fs.add_real_file('./tests/fixtures/product_response_modifications.json')
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        response = json.load(prod_response)
        response['capabilities']['ppu'] = {
            'schema': 'QT',
            'dynamic': False,
            'future': False,
            'predictive': False,
        }
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=response,
        )

        return load_workbook('./tests/fixtures/capabilities_sync.xlsx')


@pytest.fixture(scope='function')
def mocked_reports(fs):
    fs.add_real_file('./tests/fixtures/reports.json')
    with open('./tests/fixtures/reports.json') as response:
        return json.load(response)
