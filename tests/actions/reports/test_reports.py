from cnctcli.actions.reports import (
    validate_entry_points,
    validate_choices,
    validate_report_parameters,
    validate_report_definition,
    validate_report_json,
    add_info_sheet,
)

from cnctcli.config import Config
from click import ClickException
from unittest.mock import patch
from openpyxl import Workbook


import pytest


def test_validate_entry_points(mocked_reports):
    validate_entry_points(mocked_reports['reports'])
    mocked_reports['reports'].append(mocked_reports['reports'][0])

    with pytest.raises(ClickException) as e:
        validate_entry_points(mocked_reports['reports'])

    assert str(e.value) == 'There is a duplicated entrypoint on reports.json'


def test_validate_choices(mocked_reports):
    param=mocked_reports['reports'][0]['parameters'][0]
    with pytest.raises(ClickException) as e:
        validate_choices(param, 'report')

    assert 'Missing choices for parameter' in str(e.value)


def test_validate_choices_2(mocked_reports):
    param={
        "id": "rr_type",
        "type": "checkbox",
        "name": "Types of requests",
        "description": "Select the requests types you want to include in report",
        "choices": [
            {
                "no": "purchase",
                "label": "Purchase"
            }
        ]
    }

    with pytest.raises(ClickException) as e:
        validate_choices(param, 'report')

    assert 'Missing value in one of the choices for ' in str(e.value)


def test_validate_choices_3(mocked_reports):
    param={
        "id": "rr_type",
        "type": "checkbox",
        "name": "Types of requests",
        "description": "Select the requests types you want to include in report",
        "choices": [
            {
                "value": "purchase",
                "labels": "Purchase"
            }
        ]
    }

    with pytest.raises(ClickException) as e:
        validate_choices(param, 'report')

    assert 'Missing label in one of the choices for' in str(e.value)


def test_validate_report_parameters(mocked_reports):
    report = mocked_reports['reports'][0]
    del report['parameters'][0]['id']

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report, 'report')

    assert 'id' in str(e.value)


def test_validate_report_parameters_1(mocked_reports):
    report_parameters = mocked_reports['reports'][0]['parameters'][0]
    del report_parameters['type']

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report_parameters, 'report')

    assert 'type' in str(e.value)


def test_validate_report_parameters_2(mocked_reports):
    report_parameters = mocked_reports['reports'][0]['parameters'][0]
    del report_parameters['name']

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report_parameters, 'report')

    assert 'name' in str(e.value)


def test_validate_report_parameters_3(mocked_reports):
    report_parameters = mocked_reports['reports'][0]['parameters'][0]
    del report_parameters['description']

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report_parameters, 'report')

    assert 'description' in str(e.value)


def test_validate_report_parameters_4(mocked_reports):
    report_parameters = mocked_reports['reports'][0]['parameters'][0]
    report_parameters['type'] = 'FAKE'

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report_parameters, 'report')

    assert 'has a unknown parameter type' in str(e.value)


def test_validate_report_parameters_5(mocked_reports):
    report_parameters = mocked_reports['reports'][0]['parameters'][2]
    report_parameters['choices'] = [{'not': 'FAKE'}]

    with pytest.raises(ClickException) as e:
        validate_report_parameters(report_parameters, 'report')

    assert 'Missing value in one of the choices for rr_type on report report' in str(e.value)


def test_validate_report_definition(mocked_reports):
    del mocked_reports['reports'][0]['name']

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Property name not found in report' in str(e.value)


def test_validate_report_definition_2(mocked_reports):
    del mocked_reports['reports'][0]['readme_file']

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Property readme_file not found' in str(e.value)


def test_validate_report_definition_3(mocked_reports):
    mocked_reports['reports'][0]['report_spec'] = 0

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Supported report specification by Connect CLI tool is 1' in str(e.value)


def test_validate_report_definition_4(mocked_reports):
    del mocked_reports['reports'][0]['parameters'][0]['id']

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Missing id on parameters for report Fulfillment requests report' in str(e.value)


def test_validate_report_definition_5(mocked_reports):
    del mocked_reports['reports'][0]['parameters']

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Missing parameters list for report' in str(e.value)


def test_validate_report_definition_missing_template_file(mocker, mocked_reports):

    mocker.patch(
        'cnctcli.actions.reports.os.path.isfile',
        return_value=False,
    )

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Template reports/fulfillment_requests/template.xlsx not found' in str(e.value)


@patch('os.path.isfile')
def test_validate_report_definition_missing_readme_file(mock_isfile, mocked_reports):

    def side_effect(filename):
        if 'template.xlsx' in filename:
            return True
        return False

    mock_isfile.side_effect = side_effect

    with pytest.raises(ClickException) as e:
        validate_report_definition(mocked_reports['reports'][0], '/tmp')

    assert 'Readme.md' in str(e.value)


@pytest.mark.parametrize(
    ('property',),
    (
        ('name',),
        ('readme_file',),
        ('version',),
        ('reports',),
    )
)
def test_validate_report_json(property, mocked_reports):
    del mocked_reports[property]
    with pytest.raises(ClickException) as e:
        validate_report_json(mocked_reports, '/tmp')

    if property != 'reports':
        assert 'is required for reports.json' in str(e.value)
    else:
        assert "No reports declared in reports.json" in str(e.value)


def test_validate_report_json_2(mocker, mocked_reports):
    mocker.patch(
        'cnctcli.actions.reports.os.path.isfile',
        return_value=True,
    )
    validate_report_json(mocked_reports, '/tmp')


def test_add_info_sheet():
    config = Config()
    config.load('/tmp')
    config.add_account('VA-000', 'Account 0', 'Api 0', 'https://localhost/public/v1')
    wb = Workbook()

    report = {
        "name": "test"
    }

    add_info_sheet(wb.create_sheet('Info'), config, report, {}, '2020-01-01', 'report_id')

    assert wb['Info']['B4'].value == config.active.id
    assert wb['Info']['B7'].value == 'test'
