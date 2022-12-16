# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

from collections import namedtuple

from connect.client.rql import R

from connect.cli.plugins.product.api import (
    create_item,
    create_unit,
    delete_item,
    get_item,
    get_item_by_mpn,
    update_item,
)
from connect.cli.plugins.product.constants import BILLING_PERIOD, COMMITMENT, PRECISIONS
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.shared.constants import ITEMS_COLS_HEADERS


fields = (v.replace(' ', '_').lower() for v in ITEMS_COLS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class ItemSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        self._units = list(client.ns('settings').units.all())
        self._mstats = stats['Items']
        super().__init__(client, progress)

    def sync(self):  # noqa: CCR001
        ws = self._wb["Items"]

        task = self._progress.add_task('Processing item', total=ws.max_row - 1)
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 14)])
            self._progress.update(
                task,
                description=f'Processing item {data.id or data.mpn}',
                advance=1,
            )
            if data.action == '-':
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue

            if data.action == 'create':
                rql = R().mpn.eq(data.mpn)
                item = (
                    self._client.products[self._product_id]
                    .items
                    .filter(rql)
                    .first()
                )
                if item:
                    self._mstats.error(
                        f'Cannot create item: item with MPN `{data.mpn}`'
                        f' already exists with ID `{item["id"]}`.',
                        row_idx,
                    )
                    continue
                self._progress.update(
                    task,
                    description=f'Creating item {data[1]}',
                )
                try:
                    item = create_item(
                        self._client,
                        self._product_id,
                        self._get_item_payload(data),
                    )
                    self._mstats.created()
                    self._update_sheet_row(ws, row_idx, item)
                except Exception as e:
                    self._mstats.error(str(e), row_idx)

            if data.action == 'update':
                item = self._get_item(data)

                if not item:
                    field = 'ID' if data.id else 'MPN'
                    value = data.id if data.id else data.mpn
                    self._mstats.error(
                        f'Cannot update item: item with {field} `{value}` '
                        f'the item does not exist.',
                        row_idx,
                    )
                    continue

                self._progress.update(
                    task,
                    description=f"Updating item {item['id']}",
                )
                if item['status'] == 'published':
                    payload = {
                        'name': data.name,
                        'mpn': data.mpn,
                        'description': data.description,
                        'ui': {'visibility': True},
                    }
                else:
                    payload = self._get_item_payload(data)
                    if item['type'] == 'ppu':
                        del payload['period']
                try:
                    item = update_item(
                        self._client,
                        self._product_id,
                        item['id'],
                        payload,
                    )
                    self._mstats.updated()
                    self._update_sheet_row(ws, row_idx, item)
                except Exception as e:
                    self._mstats.error(str(e), row_idx)

            if data.action == 'delete':
                item = self._get_item(data)

                if not item:
                    field = 'ID' if data.id else 'MPN'
                    value = data.id if data.id else data.mpn
                    self._mstats.error(
                        f'Cannot update item: item with {field} `{value}` '
                        f'the item does not exist.',
                        row_idx,
                    )
                    continue

                self._progress.update(
                    task,
                    description=f"Deleting item {item['id']}",
                )
                try:
                    delete_item(
                        self._client,
                        self._product_id,
                        item['id'],
                    )
                    self._mstats.deleted()
                except Exception as e:
                    self._mstats.error(str(e), row_idx)
        self._progress.update(task, completed=ws.max_row - 1)

    @staticmethod
    def _validate_commitment(row):
        if row.commitment not in COMMITMENT:
            valid_commitment = ', '.join([f'`{name}`' for name in COMMITMENT])
            return [
                f'the item `Commitment` must be one between '
                f'{valid_commitment}, not `{row.commitment}`.',
            ]

        if row.type == 'ppu' and row.commitment != '-':
            return [
                f'the commitment `{row.commitment}` '
                'is invalid for `ppu` items.',
            ]

        if row.billing_period == 'onetime' and row.commitment != '-':
            return [
                f'the commitment `{row.commitment}` '
                'is invalid for `onetime` items.',
            ]

        if row.billing_period == '2 years' and row.commitment not in ('-', '4 years'):
            return [
                f'for a billing period of `2 years` the commitment '
                'must be one between `-`, `4 years`, '
                f' not {row.commitment}.',
            ]
        if row.billing_period in (
            '3 years',
            '4 years',
            '5 years',
        ) and row.commitment != '-':
            return [
                f'for a billing period of `{row.billing_period}` the commitment '
                f'must be `-`, not {row.commitment}.',
            ]

        return []

    def _validate_row(self, row):  # noqa: CCR001
        errors = []
        if row.action in ('delete', 'update'):
            if not (row.id or row.mpn):
                errors.append(
                    'one between the item `ID` or '
                    f'`MPN` is required for the `{row.action}` action.',
                )
                return errors
        if row.status == 'published' and row.action == 'delete':
            errors.append(
                'the item status must be `draft` '
                'for the `delete` action.',
            )
            return errors

        if row.action == 'create' and row.id:
            errors.append(
                'the `ID` must not be specified '
                'for the `create` action.',
            )
            return errors

        if not row.mpn:
            errors.append(
                'the item `MPN` is required.',
            )

        if not row.name:
            errors.append(
                f'the item `Name` is required for the `{row.action}` action.',
            )
        if not row.description:
            errors.append(
                f'the item `Description` is required for the `{row.action}` action.',
            )

        if row.type not in ('reservation', 'ppu'):
            errors.append(
                f'the item `Type` must be one between'
                f' `reservation` or `ppu`, not `{row.type}`.',
            )

        if row.type == 'reservation':
            if row.precision != 'integer':
                errors.append(
                    f'for items of type `reservation` the `Precision` '
                    f'must be `integer`, not `{row.precision}`.',
                )
        else:
            if row.precision not in PRECISIONS:
                valid_precision = ', '.join([f'`{name}`' for name in PRECISIONS])
                errors.append(
                    f'the item `Precision` must be one between '
                    f'{valid_precision}, not `{row.precision}`.',
                )

        if row.type == 'ppu':
            if row.billing_period != 'monthly':
                errors.append(
                    f'for items of type `ppu` the `Billing period` '
                    f'must be `monthly`, not `{row.billing_period}`.',
                )
        else:
            if row.billing_period not in BILLING_PERIOD:
                valid_period = ', '.join([f'`{name}`' for name in BILLING_PERIOD])
                errors.append(
                    f'the item `Billing period` must be one between'
                    f' {valid_period}, not `{row.billing_period}`.',
                )

        errors.extend(self._validate_commitment(row))
        return errors

    @staticmethod
    def _get_commitment_count(data):
        if data.billing_period == 'onetime':
            return 1
        if data.commitment == '-':
            return 1
        try:
            years, _ = data.commitment.split()
            years = int(years)
            if data.billing_period == 'monthly':
                return years * 12
            return years
        except:  # noqa
            return 1

    @staticmethod
    def _get_billing_period(data):
        if data.billing_period in ('onetime', 'monthly', 'yearly'):
            return data.billing_period
        count, _ = data.billing_period.split()
        return f'years_{count}'

    def _get_or_create_unit(self, data):
        for unit in self._units:
            if unit['id'] == data.unit:
                return unit['id']
            if unit['type'] == data.type and unit['description'] == data.unit:
                return unit['id']

        created = create_unit(
            self._client,
            {
                'description': data.unit,
                'type': data.type,
                'unit': 'unit' if data.type == 'reservation' else 'unit-h',
            },
        )
        return created['id']

    def _get_item(self, data):
        if data.id:
            return get_item(self._client, self._product_id, data.id)
        elif data.mpn:
            return get_item_by_mpn(self._client, self._product_id, data.mpn)

    def _get_item_payload(self, data):
        commitment = {
            'commitment': {
                'count': self._get_commitment_count(data),
            },
        }
        payload = {
            'mpn': data.mpn,
            'name': data.name,
            'description': data.description,
            'type': data.type,
            'precision': data.precision,
            'unit': {'id': self._get_or_create_unit(data)},
            'period': self._get_billing_period(data),
            'ui': {'visibility': True},
        }
        if data.type == 'reservation':
            payload.update(commitment)

        return payload

    @staticmethod
    def _update_sheet_row(ws, row_idx, item):
        ws.cell(row_idx, 1, value=item['id'])
        ws.cell(row_idx, 3, value='-')
        ws.cell(row_idx, 11, value=item['status'])
        ws.cell(row_idx, 12, value=item['events']['created']['at'])
        ws.cell(row_idx, 13, value=item['events'].get('updated', {}).get('at'))
