# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

import re
from collections import namedtuple
from functools import partial

from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.shared.constants import (
    ACTIONS_HEADERS,
)
from connect.client import ClientError

fields = (v.replace(' ', '_').lower() for v in ACTIONS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class ActionsSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        super().__init__(client, progress)
        self._mstats = stats['Actions']

    def sync(self):  # noqa: CCR001
        ws = self._wb["Actions"]
        task = self._progress.add_task('Processing action', total=ws.max_row - 1)
        actions = self._get_actions()
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 10)])
            self._progress.update(
                task,
                description=f'Processing action {data.verbose_id or data.id}',
                advance=1,
            )
            if data.action == '-':
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)

            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue

            if data.action == 'delete':
                try:
                    self._client.products[self._product_id].actions[data.verbose_id].delete()
                    self._update_sheet_row(ws, row_idx, action='delete')
                    self._mstats.deleted()
                except ClientError as e:
                    if e.status_code == 404:
                        self._mstats.deleted()
                        continue
                    self._mstats.error(str(e), row_idx)
                    continue

            payload = {
                "action": data.id,
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
                    self._update_sheet_row(ws, row_idx, action)
                    self._mstats.updated()
                except Exception as e:
                    self._mstats.error(str(e), row_idx)

            if data.action == 'create':
                try:
                    def _check_if_matches(data, x):
                        return x['action'] == data.id
                    original_action = list(filter(partial(_check_if_matches, data), actions))
                    if original_action:
                        self._updated_or_skipped(ws, row_idx, original_action[0], payload)
                        continue
                    payload['name'] = data.name
                    action = self._client.products[self._product_id].actions.create(payload)
                    self._update_sheet_row(ws, row_idx, action)
                    self._mstats.created()
                except ClientError as e:
                    self._mstats.error(str(e), row_idx)
        self._progress.update(task, completed=ws.max_row - 1)

    @staticmethod
    def _update_sheet_row(ws, row_idx, action=None):
        if isinstance(action, dict) or action is None:
            ws.cell(row_idx, 3, value='-')
            if not action:
                ws.cell(row_idx, 4, value=ws.cell(row_idx, 5).value)
            else:
                ws.cell(row_idx, 1, value=action['id'])
                ws.cell(row_idx, 4, value=action['title'])
                ws.cell(row_idx, 8, value=action['events']['created']['at'])
                ws.cell(row_idx, 9, value=action['events'].get('updated', {}).get('at'))
        if action == 'delete':
            for c in range(1, ws.max_column + 1):
                ws.cell(row_idx, c, value='')

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

    def _get_actions(self):
        return (
            self._client
            .products[
                self._product_id
            ]
            .actions
        ).all()

    def _updated_or_skipped(self, ws, row_idx, original, payload):
        original_filter = {k: v for k, v in original.items() if k in payload.keys()}
        if original_filter == payload:
            self._update_sheet_row(ws, row_idx)
            self._mstats.skipped()
        else:
            action = self._client.products[self._product_id].actions[
                original["id"]
            ].update(
                payload,
            )
            self._update_sheet_row(ws, row_idx, action)
            self._mstats.updated()
