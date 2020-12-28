from cnct import R
from interrogatio.validators import RegexValidator, RequiredValidator, Validator
from interrogatio.core.exceptions import ValidationError

import json


class ObjectValidator(Validator):

    def validate(self, value):
        if not value or value == "":
            return
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError("Introduced data is not a valid json object")


def required_validator(param, validators=None):
    if not validators:
        validators = []

    if param.get('required', False):
        validators.append(RequiredValidator(
            message="Please select at least one value"
        ))
    return validators


def single_line(param):

    return {
        'name': param['id'],
        'type': 'input',
        'question_mark': '',
        'message': f'{param["description"]}',
        'validators': required_validator(param),
    }


def object_param(param):
    validators = required_validator(param)
    validators.append(ObjectValidator())

    return {
        'name': param['id'],
        'type': 'input',
        'multiline': True,
        'default': "{}",
        'question_mark': '',
        'message': f'{param["description"]}',
        'validators': validators,
    }


def date_range(param):

    date_validator = [RegexValidator('\\d{4}-\\d{2}-\\d{2}', 'Introduced date is invalid')]

    return [
        {
            'name': f'{param["id"]}_after',
            'type': 'input',
            'message': f'{param["name"]} after:',
            'question_mark': '',
            'validators': required_validator(param, date_validator),
        },
        {
            'name': f'{param["id"]}_before',
            'type': 'input',
            'message': f'{param["name"]} before:',
            'question_mark': '',
            'validators': required_validator(param, date_validator),
        },
    ]


def date(param):

    date_validator = [RegexValidator('\\d{4}-\\d{2}-\\d{2}', 'Introduced date is invalid')]

    return {
        'name': f'{param["id"]}',
        'type': 'input',
        'message': f'{param["description"]}:',
        'question_mark': '',
        'validators': required_validator(param, date_validator),
    }


def marketplace_list(config, client, param):
    marketplaces = client.marketplaces.all()
    return {
        'name': param['id'],
        'type': 'selectmany',
        'message': f'{param["description"]}',
        'question_mark': '',
        'values': [
            (m['id'], m['name'])
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
        'message': f'{param["description"]}',
        'question_mark': '',
        'values': [
            (h['id'], h['name'])
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
        'message': f'{param["description"]}',
        'question_mark': '',
        'values': [
            (p['id'], p['name'])
            for p in products
        ],
        'validators': required_validator(param),
    }


def checkbox(param):
    values = []
    for choice in param['choices']:
        values.append(
            (choice['value'], choice['label'])
        )
    if param['type'] == 'checkbox':
        input_type = 'selectmany'
    else:
        input_type = 'selectone'

    return {
        'name': param['id'],
        'type': input_type,
        'question_mark': '',
        'message': f'{param["description"]}',
        'values': values,
        'validators': required_validator(param),
    }


static_params = {
    "checkbox": checkbox,
    "choice": checkbox,
    "single_line": single_line,
    "object": object_param,
}

dynamic_params = {
    "product": product_list,
    "marketplace": marketplace_list,
    "hub": hub_list,
}

date_params = {
    "date_range": date_range,
    "date": date,
}
