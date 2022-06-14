import json
from copy import deepcopy


def cleanup_product_for_update(product):
    del product['icon']
    ppu = product['capabilities'].get('ppu', False)
    if product['capabilities']['subscription'] and 'schema' in product['capabilities']['subscription']:
        del product['capabilities']['subscription']['schema']
    if ppu and 'predictive' in ppu:
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
