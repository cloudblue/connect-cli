import pytest
from click import ClickException 
from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import DateTimeRangeValidator, DateTimeValidator, RequiredValidator

from connect.cli.core.config import Config
from connect.cli.plugins.report.wizard import (
    checkbox,
    date,
    date_range,
    generate_summary,
    get_report_inputs,
    handle_param_input,
    hub_list,
    marketplace_list,
    object_param,
    ObjectValidator,
    product_list,
    required_validator,
    single_line,
)
from connect.client import ConnectClient


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
    assert len(result) == 5
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
    assert len(result) == 5
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
                "label": "Purchase",
            },
            {
                "value": "change",
                "label": "Change",
            },
            {
                "value": "suspend",
                "label": "Suspend",
            },
            {
                "value": "resume",
                "label": "Resume",
            },
            {
                "value": "cancel",
                "label": "Cancel",
            },
        ],
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
                "label": "Purchase",
            },
            {
                "value": "change",
                "label": "Change",
            },
            {
                "value": "suspend",
                "label": "Suspend",
            },
            {
                "value": "resume",
                "label": "Resume",
            },
            {
                "value": "cancel",
                "label": "Cancel",
            },
        ],
    }

    result = checkbox(param)

    assert result['type'] == 'selectone'
    assert len(result['values']) == len(param['choices'])


def test_marketplace_list(mocked_responses):
    param = {
        "id": "mkp",
        "type": "marketplace",
        "name": "Marketplaces",
        "description": "Select the marketplaces you want to include in report",
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
            },
        ],
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
        "description": "Select the marketplaces you want to include in report",
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
                    },
                ],
            },
        ],
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
        json=[mocked_product_response],
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
        json=[mocked_product_response],
    )

    result = product_list(config.active, client, param)
    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('PRD-276-377-545', 'My Product (PRD-276-377-545)')


def test_get_report_inputs_cancel_report(mocker):
    mocked_report = mocker.MagicMock()
    mocked_report.get_parameters.return_value = [{'id': 'a_param'}]
    mocker.patch('connect.cli.plugins.report.wizard.generate_intro')
    mocker.patch('connect.cli.plugins.report.wizard.handle_param_input')
    mocker.patch('connect.cli.plugins.report.wizard.dialogus', return_value=None)
    with pytest.raises(ClickException) as cv:
        get_report_inputs(None, None, mocked_report, None)
    assert str(cv.value) == 'Aborted by user input'


@pytest.mark.parametrize(
    ('answer', 'expected'),
    (
        (['a'], {'all': False, 'choices': ['a']}),
        (['a', 'b'], {'all': True, 'choices': []}),
    ),
)
def test_get_report_inputs_select_many(mocker, answer, expected):
    question = {
        'name': 'a_param',
        'label': 'Test select many',
        'type': 'selectmany',
        'description': 'Test',
        'values': [
            ('a', 'A'),
            ('b', 'B'),
        ],
    }
    mocked_report = mocker.MagicMock()
    mocked_report.get_parameters.return_value = [{'id': 'a_param', 'type': 'product'}]
    mocker.patch('connect.cli.plugins.report.wizard.generate_intro')
    mocker.patch('connect.cli.plugins.report.wizard.handle_param_input', return_value=question)
    mocker.patch('connect.cli.plugins.report.wizard.dialogus', return_value={'a_param': answer})
    inputs = get_report_inputs(None, None, mocked_report, None)
    assert inputs['a_param'] == expected


def test_get_report_inputs_other(mocker):
    question = {
        'name': 'a_param',
        'label': 'Test others',
        'type': 'input',
        'description': 'Test',
    }
    mocked_report = mocker.MagicMock()
    mocked_report.get_parameters.return_value = [{'id': 'a_param', 'type': 'single_line'}]
    mocker.patch('connect.cli.plugins.report.wizard.generate_intro')
    mocker.patch('connect.cli.plugins.report.wizard.handle_param_input', return_value=question)
    mocker.patch('connect.cli.plugins.report.wizard.dialogus', return_value={'a_param': 'a value'})
    inputs = get_report_inputs(None, None, mocked_report, None)
    assert inputs['a_param'] == 'a value'


def test_generate_summary():
    info = {
        'a_param': {
            'question': {
                'name': 'a_param',
                'label': 'Test summary',
                'type': 'input',
                'description': 'Test',
            },
            'value': 'a value',
            'formatted_value': 'a value',
        },
        'a_param2': {
            'question': {
                'name': 'a_param2',
                'label': 'Test summary 2',
                'type': 'selectmany',
                'description': 'Test',
                'values': [
                    ('a', 'A'),
                    ('b', 'B'),
                ],
            },
            'value': ['a', 'b'],
            'formatted_value': 'A, B',
        },
    }

    summary = generate_summary(info)
    assert summary == '\n'.join([
        '<b>Test summary: </b>a value',
        '<b>Test summary 2: </b>All',
    ])


def test_generate_summary_some():
    info = {
        'a_param': {
            'question': {
                'name': 'a_param',
                'label': 'Test summary',
                'type': 'input',
                'description': 'Test',
            },
            'value': 'a value',
            'formatted_value': 'a value',
        },
        'a_param2': {
            'question': {
                'name': 'a_param2',
                'label': 'Test summary 2',
                'type': 'selectmany',
                'description': 'Test',
                'values': [
                    ('a', 'A'),
                    ('b', 'B'),
                ],
            },
            'value': ['a'],
            'formatted_value': 'A',
        },
    }

    summary = generate_summary(info)
    assert summary == '\n'.join([
        '<b>Test summary: </b>a value',
        '<b>Test summary 2: </b>A',
    ])


def test_handle_param_inputs_dynamic(mocker, mocked_responses, mocked_product_response):
    mocked_active_account = mocker.MagicMock()
    mocked_active_account.is_vendor.return_value = True
    mocked_config = mocker.MagicMock(active=mocked_active_account)
    param = {
        'id': 'product',
        'type': 'product',
        'name': 'Product list',
        'description': 'Select the products you want to include in report',
    }

    client = ConnectClient(
        api_key='ApiKey X',
        endpoint='https://localhost/public/v1',
        use_specs=False,
    )
    mocked_responses.add(
        url='https://localhost/public/v1/products',
        method='GET',
        json=[mocked_product_response],
    )

    result = handle_param_input(mocked_config, client, param)

    assert result['type'] == 'selectmany'
    assert len(result['values']) == 1
    assert result['values'][0] == ('PRD-276-377-545', 'My Product (PRD-276-377-545)')


def test_handle_param_inputs_unknown():

    with pytest.raises(ClickException) as cv:
        handle_param_input(None, None, {'type': 'unknown'})

    assert str(cv.value) == 'Unknown parameter type unknown'
