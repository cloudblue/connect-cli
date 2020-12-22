from cnct import R
from interrogatio.validators import RegexValidator, RequiredValidator


def required_validator(param, validators=None):
    if not validators:
        validators = []

    if param.get('required', False):
        validators.append(RequiredValidator(
            message="Please select at least one value"
        ))
    return validators


def date_range(param):

    date_validator = [RegexValidator('\d{4}-\d{2}-\d{2}', 'Introduced date is invalid')]

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


def marketplace_list(client, param):
    marketplaces = client.marketplaces.all()
    return {
        'name': param['id'],
        'type': 'selectmany',
        'message': f'{param["name"]}',
        'question_mark': '',
        'values': [
            (m['id'], m['name'])
            for m in marketplaces
        ],
        'validators': required_validator(param),
    }


def hubs_list(client, param):
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
        'message': f'{param["name"]}',
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
    products = client.products.filter(default_query)
    return {
        'name': param['id'],
        'type': 'selectmany',
        'message': f'{param["name"]}',
        'question_mark': '',
        'values': [
            ( p['id'], p['name'])
            for p in products
        ],
        'validators': required_validator(param),
    }


def fulfillment_request_type(param):
    return {
        'name': param['id'],
        'type': 'selectmany',
        'message': f'{param["name"]}',
        'question_mark': '',
        'values': [
            ('purchase', 'Purchase'),
            ('change', 'Change'),
            ('suspend', 'Suspend'),
            ('resume', 'Resume'),
            ('cancel', 'Cancel'),
        ],
        'required': param.get('required', False),
    }


def fulfillment_request_status(param):
    return {
        'name': param['id'],
        'type': 'selectmany',
        'message': f'{param["name"]}',
        'question_mark': '',
        'values': [
            ('tiers_setup', 'Tiers Setup'),
            ('inquiring', 'Inquiring'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('failed', 'Failed'),
            ('draft', 'Draft'),
        ],
        'validators': required_validator(param),
    }


def connection_type(param):
    return {
        'name': param['id'],
        'type': 'selectmany',
        'question_mark': '',
        'message': f'{param["name"]}',
        'values': [
            ('preview', 'Preview'),
            ('test', 'Test'),
            ('production', 'Production'),
        ],
        'validators': required_validator(param),
    }
