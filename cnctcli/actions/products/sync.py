# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2020 Ingram Micro. All Rights Reserved.

from zipfile import BadZipFile

from click import ClickException

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from tqdm import trange

from cnctcli.actions.products.constants import ITEMS_COLS_HEADERS
from cnctcli.api.products import (
    create_item,
    get_item,
    get_item_by_mpn,
    get_product,
    update_item,
)


def _open_workbook(input_file):
    try:
        return load_workbook(input_file)
    except InvalidFileException as ife:
        raise ClickException(str(ife))
    except BadZipFile:
        raise ClickException(f'{input_file} is not a valid xlsx file.')


def _validate_item_sheet(ws):
    cels = ws['A1': 'H1']
    for cel in cels[0]:
        if cel.value != ITEMS_COLS_HEADERS[cel.column_letter]:
            raise ClickException(
                f'Invalid input file: column {cel.column_letter} '
                f'must be {ITEMS_COLS_HEADERS[cel.column_letter]}'
            )


def _get_item_payload(data):
    if data[3] is True:
        # reservation
        period = 'monthly'
        if data[2].lower() == 'yearly':
            period = 'yearly'
        if data[2].lower() == 'onetime':
            period = 'onetime'
        return {
            'name': data[0],
            'mpn': data[1],
            'description': data[4],
            'ui': {'visibility': True},
            'commitment': {
                'count': 12 if data[5] is True else 1,
            },
            'unit': {'id': data[6]},
            'type': 'reservation',
            'period': period,
        }
    else:
        # PPU
        return {
            'name': data[0],
            'mpn': data[1],
            'description': data[4],
            'ui': {'visibility': True},
            'unit': {'id': data[6]},
            'type': 'ppu',
            'precision': 'decimal(2)',
        }


def validate_input_file(api_url, api_key, input_file):
    wb = _open_workbook(input_file)
    if len(wb.sheetnames) != 2:
        raise ClickException('Invalid input file: not enough sheets.')
    product_id = wb.active['B5'].value
    get_product(api_url, api_key, product_id)

    ws = wb[wb.sheetnames[1]]
    _validate_item_sheet(ws)

    return product_id, wb


def sync_product(api_url, api_key, product_id, wb):
    ws = wb[wb.sheetnames[1]]
    row_indexes = trange(2, ws.max_row + 1, position=0)
    for row_idx in row_indexes:
        data = [ws.cell(row_idx, col_idx).value for col_idx in range(1, 9)]
        row_indexes.set_description(f'Processing item {data[7] or data[1]}')
        if data[7]:
            item = get_item(api_url, api_key, product_id, data[7])
        elif data[1]:
            item = get_item_by_mpn(api_url, api_key, product_id, data[1])
        else:
            raise ClickException(
                f'Invalid item at row {row_idx}: '
                'one between MPN or Connect Item ID must be specified.'
            )
        if item:
            row_indexes.set_description(f"Updating item {item['id']}")
            update_item(
                api_url,
                api_key,
                product_id,
                item['id'],
                {
                    'name': data[0],
                    'mpn': data[1],
                    'description': data[4],
                    'ui': {'visibility': True},
                },
            )
            continue
        row_indexes.set_description(f"Creating item {data[1]}")
        item = create_item(api_url, api_key, product_id, _get_item_payload(data))
        ws.cell(row_idx, 8, value=item['id'])
