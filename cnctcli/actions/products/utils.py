from cnctcli.actions.products.constants import (
    ITEMS_COLS_HEADERS,
    PARAMS_COLS_HEADERS,
    MEDIA_COLS_HEADERS,
    CAPABILITIES_COLS_HEADERS,
    STATIC_LINK_HEADERS,
    TEMPLATES_HEADERS,
    CONFIGURATION_HEADERS,
    ACTIONS_HEADERS,
)


def get_col_limit_by_ws_type(ws_type):
    if ws_type == 'items':
        return 'M'
    elif ws_type == 'params':
        return 'L'
    elif ws_type == 'media':
        return 'F'
    elif ws_type == 'capabilities':
        return 'C'
    elif ws_type == 'static_links':
        return 'D'
    elif ws_type == 'templates':
        return 'F'
    elif ws_type == 'configurations':
        return 'G'
    elif ws_type == 'actions':
        return 'G'
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


class SheetNotFoundError(Exception):
    pass
