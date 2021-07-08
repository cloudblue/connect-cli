import json
import os
from shutil import copy2

import pytest
import responses
import toml
from fs.tempfs import TempFS
from openpyxl import load_workbook

from connect.cli.core.base import cli
from connect.cli.core.plugins import load_plugins

from tests.data import CONFIG_DATA


@pytest.fixture(scope='function')
def fs():
    return TempFS()


@pytest.fixture(scope='session')
def ccli():
    load_plugins(cli)
    return cli


@pytest.fixture(scope='function')
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'connect.cli.core.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )


@pytest.fixture(scope='function')
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope='function')
def mocked_product_response():
    with open('./tests/fixtures/product_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_categories_response():
    with open('./tests/fixtures/categories_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_media_response(fs):
    with open('./tests/fixtures/media_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_templates_response(fs):
    with open('./tests/fixtures/templates_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_items_response(fs):
    with open('./tests/fixtures/items_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_ordering_params_response(fs):
    with open('./tests/fixtures/ordering_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_fulfillment_params_response(fs):
    with open('./tests/fixtures/fulfillment_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_configuration_params_response(fs):
    with open('./tests/fixtures/configuration_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_actions_response(fs):
    with open('./tests/fixtures/actions_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def mocked_configurations_response(fs):
    with open('./tests/fixtures/configurations_response.json') as response:
        return json.load(response)


@pytest.fixture(scope='function')
def sample_product_workbook(fs):
    return load_workbook('./tests/fixtures/comparation_product.xlsx')


@pytest.fixture(scope='function')
def get_sync_items_env(fs, mocked_responses):
    with open('./tests/fixtures/units_response.json') as response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/settings/units',
            json=json.load(response),
        )
        with open('./tests/fixtures/product_response.json') as prod_response:
            mocked_responses.add(
                method='GET',
                url='https://localhost/public/v1/products/PRD-276-377-545',
                json=json.load(prod_response),
            )

            return load_workbook('./tests/fixtures/items_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_actions_env(fs, mocked_responses):
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/actions_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_capabilities_env(fs, mocked_responses):
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/capabilities_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_params_env(fs, mocked_responses):
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/params_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_config_env(fs, mocked_responses):
    with open('./tests/fixtures/product_response_modifications.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/configuration_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_templates_env(fs, mocked_responses):
    with open('./tests/fixtures/product_response.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/templates_sync.xlsx')


@pytest.fixture(scope='function')
def get_general_env(fs, mocked_responses):
    os.mkdir(f'{fs.root_path}/media')
    copy2('./tests/fixtures/image.png', f'{fs.root_path}/media/PRD-276-377-545.png')
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
                json=json.load(prod_response),
            )

        return load_workbook('./tests/fixtures/comparation_product.xlsx')


@pytest.fixture(scope='function')
def get_sync_media_env(fs, mocked_responses):
    os.mkdir(f'{fs.root_path}/media')
    copy2('./tests/fixtures/image.png', f'{fs.root_path}/media/image.png')
    with open('./tests/fixtures/product_response.json') as prod_response:
        mocked_responses.add(
            method='GET',
            url='https://localhost/public/v1/products/PRD-276-377-545',
            json=json.load(prod_response),
        )

        return load_workbook('./tests/fixtures/media_sync.xlsx')


@pytest.fixture(scope='function')
def get_sync_capabilities_env_ppu_enabled(fs, mocked_responses):
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
    with open('./tests/fixtures/reports.json') as response:
        return json.load(response)


@pytest.fixture
def mocked_customer():
    with open('./tests/fixtures/customer/customer.json') as response:
        return json.load(response)


@pytest.fixture
def mocked_reseller():
    with open('./tests/fixtures/customer/reseller.json') as response:
        return json.load(response)


@pytest.fixture
def customers_workbook(fs):
    return load_workbook('./tests/fixtures/customer/customers.xlsx')


@pytest.fixture(scope='function')
def mocked_extension_project_descriptor(fs):
    return toml.load('./tests/fixtures/extensions/basic_ext/pyproject.toml')


@pytest.fixture(scope='function')
def mocked_extension_descriptor(fs):
    with open('./tests/fixtures/extensions/basic_ext/connect_ext/extension.json') as response:
        return json.load(response)
