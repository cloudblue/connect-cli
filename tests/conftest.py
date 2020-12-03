import json

import pytest

import responses

from tests.data import CONFIG_DATA
from openpyxl import load_workbook

@pytest.fixture()
def config_mocker(mocker):
    mocker.patch('os.path.isfile', return_value=True)
    return mocker.patch(
        'cnctcli.config.open',
        mocker.mock_open(read_data=json.dumps(CONFIG_DATA)),
    )


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def mocked_product_response(fs):
    fs.add_real_file('./tests/fixtures/product_response.json')
    with open('./tests/fixtures/product_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_categories_response(fs):
    fs.add_real_file('./tests/fixtures/categories_response.json')
    with open('./tests/fixtures/categories_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_media_response(fs):
    fs.add_real_file('./tests/fixtures/media_response.json')
    with open('./tests/fixtures/media_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_templates_response(fs):
    fs.add_real_file('./tests/fixtures/templates_response.json')
    with open('./tests/fixtures/templates_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_items_response(fs):
    fs.add_real_file('./tests/fixtures/items_response.json')
    with open('./tests/fixtures/items_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_ordering_params_response(fs):
    fs.add_real_file('./tests/fixtures/ordering_parameters_response.json')
    with open('./tests/fixtures/ordering_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_fulfillment_params_response(fs):
    fs.add_real_file('./tests/fixtures/fulfillment_parameters_response.json')
    with open('./tests/fixtures/fulfillment_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_configuration_params_response(fs):
    fs.add_real_file('./tests/fixtures/configuration_parameters_response.json')
    with open('./tests/fixtures/configuration_parameters_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_actions_response(fs):
    fs.add_real_file('./tests/fixtures/actions_response.json')
    with open('./tests/fixtures/actions_response.json') as response:
        return json.load(response)


@pytest.fixture()
def mocked_configurations_response(fs):
    fs.add_real_file('./tests/fixtures/configurations_response.json')
    with open('./tests/fixtures/configurations_response.json') as response:
        return json.load(response)


@pytest.fixture()
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
