import json
from copy import deepcopy

from connect.cli.plugins.product.constants import (
    ACTIONS_HEADERS,
    CAPABILITIES_COLS_HEADERS,
    CONFIGURATION_HEADERS,
    ITEMS_COLS_HEADERS,
    MEDIA_COLS_HEADERS,
    PARAMS_COLS_HEADERS,
    STATIC_LINK_HEADERS,
    TEMPLATES_HEADERS,
)


def get_col_limit_by_ws_type(ws_type):
    if ws_type == 'items':
        return 'M'
    elif ws_type == 'params':
        return 'N'
    elif ws_type == 'media':
        return 'F'
    elif ws_type == 'capabilities':
        return 'C'
    elif ws_type == 'static_links':
        return 'D'
    elif ws_type == 'templates':
        return 'H'
    elif ws_type == 'configurations':
        return 'I'
    elif ws_type == 'actions':
        return 'I'
    return 'Z'


def get_ws_type_by_worksheet_name(ws_name):
    if ws_name == 'Items':
        return 'items'
    elif ws_name == "Ordering Parameters":
        return 'params'
    elif ws_name == 'Fulfillment Parameters':
        return 'params'
    elif ws_name == 'Configuration Parameters':
        return 'params'
    elif ws_name == 'Media':
        return 'media'
    elif ws_name == 'Capabilities':
        return 'capabilities'
    elif ws_name == 'Embedding Static Resources':
        return 'static_links'
    elif ws_name == 'Templates':
        return 'templates'
    elif ws_name == 'Configuration':
        return 'configurations'
    elif ws_name == 'Actions':
        return 'actions'
    return None


def get_col_headers_by_ws_type(ws_type):
    if ws_type == 'items':
        return ITEMS_COLS_HEADERS
    elif ws_type == 'params':
        return PARAMS_COLS_HEADERS
    elif ws_type == 'media':
        return MEDIA_COLS_HEADERS
    elif ws_type == 'capabilities':
        return CAPABILITIES_COLS_HEADERS
    elif ws_type == 'static_links':
        return STATIC_LINK_HEADERS
    elif ws_type == 'templates':
        return TEMPLATES_HEADERS
    elif ws_type == 'configurations':
        return CONFIGURATION_HEADERS
    elif ws_type == 'actions':
        return ACTIONS_HEADERS


def cleanup_product_for_update(product):
    del product['icon']
    if product['capabilities']['subscription'] and 'schema' in product['capabilities']['subscription']:
        del product['capabilities']['subscription']['schema']
    if product['capabilities']['ppu'] and 'predictive' in product['capabilities']['ppu']:
        del product['capabilities']['ppu']['predictive']
    return product


def get_json_object_for_param(original_param):
    param = deepcopy(original_param)
    del param['id']
    del param['name']
    del param['title']
    del param['description']
    del param['phase']
    del param['scope']
    del param['type']
    del param['constraints']['required']
    del param['constraints']['unique']
    del param['constraints']['hidden']
    del param['position']
    del param['events']

    return json.dumps(param, indent=4, sort_keys=True)


class ParamSwitchNotSupported(Exception):
    pass
