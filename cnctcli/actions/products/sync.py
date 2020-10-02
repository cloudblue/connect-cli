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
    create_unit,
    get_item,
    get_item_by_mpn,
    get_product,
    get_units,
    update_item,
)


class ProductSynchronizer:
    def __init__(self, endpoint, api_key, silent):
        self._endpoint = endpoint
        self._api_key = api_key
        self._silent = silent
        self._units = get_units(self._endpoint, self._api_key)
        self._product_id = None
        self._wb = None

    def _open_workbook(self, input_file):
        try:
            self._wb = load_workbook(input_file)
        except InvalidFileException as ife:
            raise ClickException(str(ife))
        except BadZipFile:
            raise ClickException(f'{input_file} is not a valid xlsx file.')

    def _validate_item_sheet(self, ws):
        cels = ws['A1': 'H1']
        for cel in cels[0]:
            if cel.value != ITEMS_COLS_HEADERS[cel.column_letter]:
                raise ClickException(
                    f'Invalid input file: column {cel.column_letter} '
                    f'must be {ITEMS_COLS_HEADERS[cel.column_letter]}'
                )

    def _get_commitment_count(self, data):
        period = data[7]
        if period == 'onetime':
            return 1
        if data[8] == '-':
            return 1
        try:
            years, _ = data[8].split()
            years = int(years)
            if period == 'monthly':
                return years * 12
            return years
        except:  # noqa
            return 1

    def _get_or_create_unit(self, data):
        for unit in self._units:
            if unit['id'] == data[6]:
                return unit['id']
            if unit['type'] == data[4] and unit['description'] == data[6]:
                return unit['id']

        created = create_unit(
            self._endpoint,
            self._api_key,
            {
                'description': data[6],
                'type': data[4],
                'unit': 'unit' if data[4] == 'reservation' else 'unit-h'
            },
        )
        return created['id']

    def _get_item_payload(self, data):
        commitment = {
            'commitment': {
                'count': self._get_commitment_count(data),
            },
        }
        payload = {
            'mpn': data[1],
            'name': data[2],
            'description': data[3],
            'type': data[4],
            'precision': data[5],
            'unit': {'id': self._get_or_create_unit(data)},
            'period': data[7],
            'ui': {'visibility': True},
        }
        if data[4] == 'reservation':
            payload.update(commitment)

        return payload

    def _update_sheet_row(self, ws, row_idx, item):
        ws.cell(row_idx, 1, value=item['id'])
        ws.cell(row_idx, 10, value=item['status'])
        ws.cell(row_idx, 11, value=item['events']['created']['at'])
        ws.cell(row_idx, 12, value=item['events'].get('updated', {}).get('at'))

    def validate_input_file(self, input_file):
        self._open_workbook(input_file)
        if len(self._wb.sheetnames) != 2:
            raise ClickException('Invalid input file: not enough sheets.')
        ws = self._wb[self._wb.sheetnames[0]]
        product_id = ws['B5'].value
        get_product(self._endpoint, self._api_key, product_id)
        ws = self._wb[self._wb.sheetnames[1]]
        self._validate_item_sheet(ws)

        self._product_id = product_id
        return self._product_id

    def sync_product(self):
        ws = self._wb[self._wb.sheetnames[1]]
        row_indexes = trange(2, ws.max_row + 1, position=0, disable=self._silent)
        for row_idx in row_indexes:
            data = [ws.cell(row_idx, col_idx).value for col_idx in range(1, 13)]
            row_indexes.set_description(f'Processing item {data[0] or data[1]}')
            if data[0]:
                item = get_item(self._endpoint, self._api_key, self._product_id, data[0])
            elif data[1]:
                item = get_item_by_mpn(self._endpoint, self._api_key, self._product_id, data[1])
            else:
                raise ClickException(
                    f'Invalid item at row {row_idx}: '
                    'one between MPN or Connect Item ID must be specified.'
                )
            if item:
                row_indexes.set_description(f"Updating item {item['id']}")
                if item['status'] == 'published':
                    payload = {
                        'name': data[2],
                        'mpn': data[1],
                        'description': data[3],
                        'ui': {'visibility': True},
                    }
                else:
                    payload = self._get_item_payload(data)
                    if item['type'] == 'ppu':
                        del payload['period']
                update_item(
                    self._endpoint,
                    self._api_key,
                    self._product_id,
                    item['id'],
                    payload,
                )
                self._update_sheet_row(ws, row_idx, item)
                continue
            row_indexes.set_description(f"Creating item {data[1]}")
            item = create_item(
                self._endpoint,
                self._api_key,
                self._product_id,
                self._get_item_payload(data),
            )
            self._update_sheet_row(ws, row_idx, item)

    def save(self, output_file):
        self._wb.save(output_file)
