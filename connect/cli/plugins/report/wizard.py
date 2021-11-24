import json
import datetime
import time

from click import ClickException
from interrogatio import dialogus
from interrogatio.validators import (
    DateTimeRangeValidator,
    DateTimeValidator,
    RequiredValidator,
    Validator,
)
from interrogatio.core.exceptions import ValidationError

from connect.cli.plugins.report.utils import convert_to_utc_input
from connect.client import R


class ObjectValidator(Validator):

    def validate(self, value, context=None):
        if not value:
            return
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError('Introduced data is not a valid json object')


def required_validator(param, validators=None):
    if not validators:
        validators = []

    if param.get('required', False):
        validators.append(RequiredValidator(
            message='Please select at least one value',
        ))
    return validators


def single_line(param):

    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'input',
        'description': f'{param["description"]}',
        'validators': required_validator(param),
    }


def object_param(param):
    validators = required_validator(param)
    validators.append(ObjectValidator())

    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'input',
        'multiline': True,
        'default': '{}',  # noqa
        'description': f'{param["description"]}',
        'validators': validators,
    }


def date_range(param):
    note = '* Dates must be input in your local (UTC{offset}) {tz} timezone.'.format(
        offset=time.strftime('%z'),
        tz=datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo,
    )
    description = '{param}\n\n\n{note}\n\n{input_format}'.format(
        param=param['description'],
        note=note,
        input_format='Input format must be YYYY-MM-DD.',
    )
    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'daterange',
        'description': description,
        'validators': required_validator(param, [DateTimeRangeValidator()]),
    }


def date(param):

    date_validator = [DateTimeValidator(
        format_pattern='%Y-%m-%d',
    )]

    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'date',
        'description': f'{param["description"]}:',
        'validators': required_validator(param, date_validator),
    }


def marketplace_list(config, client, param):
    marketplaces = client.marketplaces.all()
    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'selectmany',
        'description': f'{param["description"]} ({param["id"]})',
        'values': [
            (m['id'], f'{m["name"]} ({m["id"]})')
            for m in marketplaces
        ],
        'formatting_template': '${label}',
        'validators': required_validator(param),
    }


def hub_list(config, client, param):
    marketplaces = client.marketplaces.all()
    hub_ids = []
    hubs = []
    for marketplace in marketplaces:
        if 'hubs' in marketplace:
            for hub in marketplace['hubs']:
                if hub['hub']['id'] not in hub_ids:
                    hub_ids.append(hub['hub']['id'])
                    hubs.append(hub['hub'])

    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'selectmany',
        'description': f'{param["description"]}',
        'values': [
            (h['id'], f'{h["name"]} ({h["id"]})')
            for h in hubs
        ],
        'formatting_template': '${label}',
        'validators': required_validator(param),
    }


def product_list(config, client, param):
    if config.is_vendor():
        default_query = R().visibility.owner.eq(True) & R().version.null(True)
    else:
        default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)
    products = client.products.filter(default_query).order_by('name')
    return {
        'name': param['id'],
        'label': param['name'],
        'type': 'selectmany',
        'description': f'{param["description"]}',
        'values': [
            (p['id'], f'{p["name"]} ({p["id"]})')
            for p in products
        ],
        'formatting_template': '${label}',
        'validators': required_validator(param),
    }


def checkbox(param):
    values = []
    for choice in param['choices']:
        values.append(
            (choice['value'], choice['label']),
        )
    if param['type'] == 'checkbox':
        input_type = 'selectmany'
    else:
        input_type = 'selectone'

    return {
        'name': param['id'],
        'label': param['name'],
        'type': input_type,
        'description': f'{param["description"]}',
        'values': values,
        'validators': required_validator(param),
        'formatting_template': '${label}',
    }


static_params = {
    'checkbox': checkbox,
    'choice': checkbox,
    'single_line': single_line,
    'object': object_param,
}

dynamic_params = {
    'product': product_list,
    'marketplace': marketplace_list,
    'hub': hub_list,
}

date_params = {
    'date_range': date_range,
    'date': date,
}


def handle_param_input(config, client, param):
    if date_params.get(param['type']):
        handler = date_params[param['type']]
        return handler(param)

    if dynamic_params.get(param['type']):
        handler = dynamic_params[param['type']]
        return handler(config.active, client, param)
    if static_params.get(param['type']):
        handler = static_params[param['type']]
        return handler(param)

    raise ClickException(f'Unknown parameter type {param["type"]}')


def generate_intro(config, report, output_format):
    output_formats = {
        format.id: format.description
        for format in report.renderers
    }
    intro = """Welcome to the Connect CLI Report execution utility.

<b><blue>Account</blue></b>
    <b>Id:</b> {account_id}
    <b>Name:</b> {account_name}
    <b>Type:</b> {account_type}

<b><blue>Report</blue></b>
    <b>Name:</b> {report_name}
    <b>Output format:</b> {output_format}
""".format(
        account_id=config.active.id,
        account_name=config.active.name,
        account_type='Vendor' if config.active.is_vendor() else 'Distributor',
        report_name=report.name,
        output_format=output_formats[output_format],
    )
    return intro


def generate_summary(data):
    summary = []
    for info in data.values():
        label = info['question'].get('label')
        value = ''
        if info['question']['type'] in ('selectone', 'selectmany'):
            if len(info['value']) == len(info['question']['values']):
                value = 'All'
            else:
                value = info['formatted_value']
        else:
            value = info['formatted_value']
        summary.append(f'<b>{label}: </b>{value}')
    return '\n'.join(summary)


def get_report_inputs(config, client, report, output_format):
    parameters = report.get_parameters()
    if not parameters:
        return {}
    parameters_values = {}
    questions = {}
    for param in parameters:
        questions[param['id']] = handle_param_input(config, client, param)

    answers = dialogus(
        list(questions.values()),
        f'Generate report {report.name}',
        intro=generate_intro(config, report, output_format),
        summary=generate_summary,
        finish_text='Run',
        previous_text='Back',
    )

    if not answers:
        raise ClickException('Aborted by user input')

    for param in parameters:
        value = answers[param['id']]
        if param['type'] == 'date_range':
            parameters_values[param['id']] = {
                'after': convert_to_utc_input(value['from']),
                'before': convert_to_utc_input(value['to']),
            }
        elif questions[param['id']]['type'] == 'selectmany':
            if len(questions[param['id']]['values']) == len(value):
                parameters_values[param['id']] = {
                    'all': True,
                    'choices': [],
                }
            else:
                parameters_values[param['id']] = {
                    'all': False,
                    'choices': value,
                }
        else:
            parameters_values[param['id']] = value

    return parameters_values
