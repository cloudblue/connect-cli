from cnctcli.actions.reports_params import (
    ObjectValidator,
    required_validator,
    single_line,
    object_param,
    date_range,
    date,
    checkbox,
    marketplace_list,
    hub_list,
    product_list,
)

from cnctcli.config import Config
from cnct import ConnectClient
from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import RequiredValidator, DateTimeValidator, DateTimeRangeValidator


import pytest


def test_validator():
    validator = ObjectValidator()
    assert validator.validate(None) is None


def test_validator_1():
    validator = ObjectValidator()
    json_string = '{"test": "none"}'
    assert validator.validate(json_string) is None


def test_validator_2():
    validator = ObjectValidator()
    json_string = '{"test":'

    with pytest.raises(ValidationError) as e:
        validator.validate(json_string)

    assert 'Introduced data is not a valid json object' in str(e.value)


def test_required_validator(mocked_reports):
    param = mocked_reports['reports'][0]['parameters'][0]
    result = required_validator(param)

    assert isinstance(result[0], RequiredValidator)


def test_single_line():
    param = {
      "id": "date",
      "type": "single_line",
      "name": "Report period",
      "description": "Provide the time period to create the report",
      "required": True,
    }

    result = single_line(param)
    assert result['name'] == 'date'
    assert result['type'] == 'input'
    assert result['description'] == param['description']
    assert isinstance(result['validators'][0], RequiredValidator)


def test_object_param():
    param = {
        "id": "id",
        "type": "object",
        "name": "Report period",
        "description": "Provide the time period to create the report",
        "required": True,
    }

    result = object_param(param)
    assert result['name'] == 'id'
    assert result['type'] == 'input'
    assert result['description'] == param['description']
    assert result['multiline'] is True
    assert isinstance(result['validators'][0], RequiredValidator)
    assert isinstance(result['validators'][1], ObjectValidator)


def test_date_range():
    param = {
        "id": "date",
        "type": "date_range",
        "name": "Report period",
        "description": "Provide the time period to create the report",
        "required": True,
    }

    result = date_range(param)
    assert len(result) == 4
    assert isinstance(result['validators'][0], DateTimeRangeValidator)
    assert isinstance(result['validators'][1], RequiredValidator)


def test_date():
    param = {
        "id": "date",
        "type": "date",
        "name": "Report date",
        "description": "Provide the time period to create the report",
        "required": True,
    }

    result = date(param)
    assert len(result) == 4
    assert isinstance(result['validators'][1], RequiredValidator)
    assert isinstance(result['validators'][0], DateTimeValidator)


def test_checkbox():
    param = {
      "id": "rr_type",
      "type": "checkbox",
      "name": "Types of requests",
      "description": "Select the requests types you want to include in report",
      "choices": [
        {
          "value": "purchase",
          "label": "Purchase"
        },
        {
          "value": "change",
          "label": "Change"
        },
        {
          "value": "suspend",
          "label": "Suspend"
        },
        {
          "value": "resume",
          "label": "Resume"
        },
        {
          "value": "cancel",
          "label": "Cancel"
        }
      ]
    }

    result = checkbox(param)

    assert result['type'] == 'selectmany'
    assert len(result['values']) == len(param['choices'])


def test_checkbox_2():
    param = {
      "id": "rr_type",
      "type": "choice",
      "name": "Types of requests",
      "description": "Select the requests types you want to include in report",
      "choices": [
        {
          "value": "purchase",
          "label": "Purchase"
        },
        {
          "value": "change",
          "label": "Change"
        },
        {
          "value": "suspend",
          "label": "Suspend"
        },
        {
          "value": "resume",
          "label": "Resume"
        },
        {
          "value": "cancel",
          "label": "Cancel"
        }
      ]
    }

    result = checkbox(param)

    assert result['type'] == 'selectone'
    assert len(result['values']) == len(param['choices'])


def test_marketplace_list(mocked_responses):
    param = {
      "id": "mkp",
      "type": "marketplace",
      "name": "Marketplaces",
      "description": "Select the marketplaces you want to include in report"
    }

    config = Config()
    config.load('/tmp')
    config.add_account('VA-000', 'Account 0', 'Api 0', 'https://localhost/public/v1')

    client = ConnectClient(
        api_key='ApiKey X',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )

    mocked_responses.add(
        url='https://localhost/public/v1/marketplaces',
        method='GET',
        json=[
            {
                "id": "MKP-1",
                "name": "Marketplace",
            }
        ]
    )

    result = marketplace_list(config, client, param)
    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('MKP-1', 'Marketplace (MKP-1)')


def test_hub_list(mocked_responses):
    param = {
      "id": "mkp",
      "type": "marketplace",
      "name": "Marketplaces",
      "description": "Select the marketplaces you want to include in report"
    }

    config = Config()
    config.load('/tmp')
    config.add_account('VA-000', 'Account 0', 'Api 0', 'https://localhost/public/v1')

    client = ConnectClient(
        api_key='ApiKey X',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )

    mocked_responses.add(
        url='https://localhost/public/v1/marketplaces',
        method='GET',
        json=[
            {
                "id": "MKP-1",
                "name": "Marketplace",
                "hubs": [
                    {
                        "hub": {
                            "id": "hub1",
                            "name": "my_hub",
                        },
                    }
                ]
            }
        ]
    )

    result = hub_list(config, client, param)
    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('hub1', 'my_hub (hub1)')


def test_product(mocked_responses, mocked_product_response):
    param = {
       "id": "product",
       "type": "product",
       "name": "Product list",
       "description": "Select the products you want to include in report",
    }

    config = Config()
    config.load('/tmp')
    config.add_account('VA-000', 'Account 0', 'Api 0', 'https://localhost/public/v1')

    client = ConnectClient(
        api_key='ApiKey X',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )

    mocked_responses.add(
        url='https://localhost/public/v1/products',
        method='GET',
        json=[mocked_product_response]
    )

    result = product_list(config.active, client, param)
    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('PRD-276-377-545', 'My Product (PRD-276-377-545)')


def test_product_2(mocked_responses, mocked_product_response):
    param = {
       "id": "product",
       "type": "product",
       "name": "Product list",
       "description": "Select the products you want to include in report",
    }

    config = Config()
    config.load('/tmp')
    config.add_account('PA-000', 'Account 0', 'Api 0', 'https://localhost/public/v1')

    client = ConnectClient(
        api_key='ApiKey X',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )

    mocked_responses.add(
        url='https://localhost/public/v1/products',
        method='GET',
        json=[mocked_product_response]
    )

    result = product_list(config.active, client, param)
    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('PRD-276-377-545', 'My Product (PRD-276-377-545)')
