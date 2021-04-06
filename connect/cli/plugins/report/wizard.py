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

    def validate(self, value):
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
        'type': 'input',
        'description': f'{param["description"]}',
        'validators': required_validator(param),
    }


def object_param(param):
    validators = required_validator(param)
    validators.append(ObjectValidator())

    return {
        'name': param['id'],
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
        'type': 'date',
        'description': f'{param["description"]}:',
        'validators': required_validator(param, date_validator),
    }


def marketplace_list(config, client, param):
    marketplaces = client.marketplaces.all()
    return {
        'name': param['id'],
        'type': 'selectmany',
        'description': f'{param["description"]} ({param["id"]})',
        'values': [
            (m['id'], f'{m["name"]} ({m["id"]})')
            for m in marketplaces
        ],
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
        'type': 'selectmany',
        'description': f'{param["description"]}',
        'values': [
            (h['id'], f'{h["name"]} ({h["id"]})')
            for h in hubs
        ],
        'validators': required_validator(param),
    }


def product_list(config, client, param):
    if config.id.startswith('VA'):
        default_query = R().visibility.owner.eq(True) & R().version.null(True)
    else:
        default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)
    products = client.products.filter(default_query).order_by('name')
    return {
        'name': param['id'],
        'type': 'selectmany',
        'description': f'{param["description"]}',
        'values': [
            (p['id'], f'{p["name"]} ({p["id"]})')
            for p in products
        ],
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
        'type': input_type,
        'description': f'{param["description"]}',
        'values': values,
        'validators': required_validator(param),
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
    questions = []
    if date_params.get(param['type']):
        handler = date_params[param['type']]
        questions.append(
            handler(param),
        )
    elif dynamic_params.get(param['type']):
        handler = dynamic_params[param['type']]
        questions.append(
            handler(config.active, client, param),
        )
    elif static_params.get(param['type']):
        handler = static_params[param['type']]
        questions.append(
            handler(param),
        )
    else:
        raise ClickException(f'Unknown parameter type {param["type"]}')

    return questions


def get_report_inputs(config, client, parameters):
    parameters_values = {}
    i = 0
    for param in parameters:
        questions = handle_param_input(config, client, param)

        answers = dialogus(
            questions,
            param['name'],
            confirm='Run' if i == len(parameters) else 'Next',
        )

        if not answers:
            raise ClickException('Aborted by user input')

        if param['type'] == 'date_range':
            if answers[param['id']]['from']:
                after_str = answers[param['id']]['from']
                before_str = answers[param['id']]['to']
                after = convert_to_utc_input(after_str)
                before = convert_to_utc_input(before_str)
                parameters_values[param['id']] = {
                    'after': after,
                    'before': before,
                }
            continue
        elif (
            questions[0]['type'] == 'selectmany'
            and len(questions[0]['values']) == len(answers[param['id']])
        ):
            parameters_values[param['id']] = {
                'all': True,
                'choices': [],
            }
        elif (
            questions[0]['type'] == 'selectmany'
            and len(questions[0]['values']) != len(answers[param['id']])
        ):
            parameters_values[param['id']] = {
                'all': False,
                'choices': answers[param['id']],
            }
        else:
            parameters_values[param['id']] = answers[param['id']]
        i += 1
    return parameters_values
