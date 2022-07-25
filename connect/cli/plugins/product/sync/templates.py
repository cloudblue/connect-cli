# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

from collections import namedtuple

from connect.cli.plugins.shared.constants import TEMPLATES_HEADERS
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.client import ClientError

fields = (v.replace(' ', '_').lower() for v in TEMPLATES_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class TemplatesSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        super().__init__(client, progress)
        self._mstats = stats['Templates']
        self._action_handlers = {
            'create': self._action_create,
            'update': self._action_update,
            'delete': self._action_delete,
        }

    def sync(self):
        ws = self._wb["Templates"]

        task = self._progress.add_task('Processing Template', total=ws.max_row - 1)
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 9)])
            self._progress.update(
                task,
                description=f'Processing Template {data.id or data.title}',
                advance=1,
            )
            try:
                if data.action == '-':
                    self._mstats.skipped()
                else:
                    self._process_row(data, ws, task, row_idx)
            except Exception as e:
                self._mstats.error(str(e).split('\n'), row_idx)

    def _process_row(self, data, ws, task, row_idx):
        row_errors = self._validate_row(data)
        if row_errors:
            raise Exception('\n'.join(row_errors))
        template = self._action_handlers[data.action](data, task)
        if template:
            self._update_sheet_row(ws, row_idx, template)

    def _action_create(self, data, task):
        self._progress.update(task, description=f'Creating template {data.title}')
        payload = self._row_to_payload(data)
        template = self._client.products[self._product_id].templates.create(payload)
        self._mstats.created()
        return template

    def _action_update(self, data, task):
        self._progress.update(task, description=f'Updating template {data.id}')

        try:
            current = self._client.products[self._product_id].templates[data.id].get()
        except ClientError as e:
            if e.status_code == 404:
                raise Exception(
                    f'Cannot update template {data.id} since does not exist in the product. '
                    'Create it instead',
                ) from e
            raise e

        payload = self._row_to_payload(data)
        # check not changing scope or type before update
        if current.get('type') != payload.get('type') or current['scope'] != payload['scope']:
            raise Exception(
                f'Switching scope or type is not supported. '
                f'Original scope {current["scope"]}, requested scope {payload["scope"]}. '
                f'Original type {current.get("type")}, requested type {payload.get("type")}',
            )
        template = self._client.products[self._product_id].templates[data.id].update(payload)
        self._mstats.updated()
        return template

    def _action_delete(self, data, task):
        self._progress.update(task, description=f'Deleting template {data.id}')
        try:
            self._client.products[self._product_id].templates[data.id].delete()
        except ClientError as e:
            # if the template doesn't exist, perform as success deletion
            if e.status_code != 404:
                raise
        self._mstats.deleted()

    @staticmethod
    def _row_to_payload(data):
        template_payload = {
            'name': data.title,
            'scope': data.scope,
            'body': data.content,
        }
        if data.scope == 'asset':
            template_payload.update({
                'title': data.title,
                'type': data.type,
            })
        return template_payload

    @staticmethod
    def _update_sheet_row(ws, row_idx, template):
        ws.cell(row_idx, 1, value=template['id'])
        ws.cell(row_idx, 7, value=template['events']['created']['at'])
        ws.cell(row_idx, 8, value=template['events'].get('updated', {}).get('at'))

    @staticmethod
    def _validate_row(data):
        errors = []
        if data.scope not in ('asset', 'tier1', 'tier2'):
            errors.append(
                f'Valid scopes are `asset`, `tier1` or `tier2`, not {data.scope}',
            )
            return errors
        if data.type not in ('pending', 'fulfillment', 'inquire'):
            errors.append(
                f'Valid template types are `pending`, `fulfillment` or `inquiring`. Provided '
                f'{data.type}.',
            )
        if (data.scope == 'tier1' or data.scope == 'tier2') and data.type != 'fulfillment':
            errors.append(
                'Tier templates must be fulfillment type only',
            )
        if not data.title or not data.content:
            errors.append(
                'Title and Content are required',
            )
        if data.action == 'update' and not data.id.startswith('TL-'):
            errors.append(
                'Update operation requires template id',
            )
        return errors
