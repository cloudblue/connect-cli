# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import re
from collections import namedtuple

from tqdm import trange

from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.cli.plugins.product.constants import (
    ACTIONS_HEADERS,
)
from connect.cli.core.constants import DEFAULT_BAR_FORMAT
from connect.client import ClientError

fields = (v.replace(' ', '_').lower() for v in ACTIONS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class ActionsSynchronizer(ProductSynchronizer):

    def sync(self):  # noqa: CCR001
        ws = self._wb["Actions"]
        errors = {}
        skipped_count = 0
        created_items = []
        updated_items = []
        deleted_items = []
        row_indexes = trange(
            2, ws.max_row + 1, disable=self._silent, leave=True, bar_format=DEFAULT_BAR_FORMAT,
        )
        for row_idx in row_indexes:
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 10)])
            row_indexes.set_description(f'Processing action {data.verbose_id or data.id}')
            if data.action == '-':
                skipped_count += 1
                continue
            row_errors = self._validate_row(data)

            if row_errors:
                errors[row_idx] = row_errors
                continue

            if data.action == 'delete':
                try:
                    self._client.products[self._product_id].actions[data.verbose_id].delete()
                    deleted_items.append(data)
                except ClientError as e:
                    if e.status_code == 404:
                        deleted_items.append(data)
                        continue
                    errors[row_idx] = [str(e)]
                    continue

            payload = {
                "action": data.id,
                "name": data.name,
                "type": "button",
                "scope": data.scope,
                "description": data.description,
                "title": data.title,
            }

            if data.action == 'update':
                try:
                    action = self._client.products[self._product_id].actions[
                        data.verbose_id
                    ].update(payload)
                    updated_items.append(action)
                except Exception as e:
                    errors[row_idx] = [str(e)]

            if data.action == 'create':
                try:
                    action = self._client.products[self._product_id].actions.create(payload)
                    self._update_sheet_row(ws, row_idx, action)
                    created_items.append(action)
                except ClientError as e:
                    errors[row_idx] = [str(e)]

        return (
            skipped_count,
            len(created_items),
            len(updated_items),
            len(deleted_items),
            errors,
        )

    @staticmethod
    def _update_sheet_row(ws, row_idx, action):
        ws.cell(row_idx, 1, value=action['id'])
        ws.cell(row_idx, 8, value=action['events']['created']['at'])
        ws.cell(row_idx, 9, value=action['events'].get('updated', {}).get('at'))

    @staticmethod
    def _validate_row(data):
        errors = []
        if data.action not in ('-', 'create', 'update', 'delete'):
            errors.append(
                'Allowed action values are `-`, `create`, `update` or `delete`. '
                f'{data.action} is not valid action.',
            )
            return errors
        if data.action in ('delete', 'update') and not data.verbose_id:
            errors.append(
                f'Verbose ID is required for {data.action} action.',
            )
            return errors

        id_pattern = "^[A-Za-z0-9_-]*$"

        if not bool(re.match(id_pattern, data.id)):
            errors.append(
                f'Actions ID must contain only letters, numbers and `_`, provided {data.id}',
            )
            return errors

        if data.scope not in ('asset', 'tier1', 'tier2'):
            errors.append(
                f'Action scope must be one of `asset`, `tier1` or `tier2`. Provided {data.scope}',
            )

        return errors
