# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.

from collections import namedtuple

from tqdm import trange

from connect.cli.core.constants import DEFAULT_BAR_FORMAT
from connect.cli.plugins.product.constants import TEMPLATES_HEADERS
from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.client import ClientError

fields = (v.replace(' ', '_').lower() for v in TEMPLATES_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class TemplatesSynchronizer(ProductSynchronizer):
    def sync(self):  # noqa: CCR001
        ws = self._wb["Templates"]
        errors = {}
        skipped_count = 0
        created_items = []
        updated_items = []
        deleted_items = []

        row_indexes = trange(
            2, ws.max_row + 1, disable=self._silent, leave=True, bar_format=DEFAULT_BAR_FORMAT,
        )
        for row_idx in row_indexes:
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 9)])
            row_indexes.set_description(f'Processing Template {data.id or data.title}')
            if data.action == '-':
                skipped_count += 1
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                errors[row_idx] = row_errors
                continue
            template_data = {
                'name': data.title,
                'scope': data.scope,
                'body': data.content,
                'type': data.type,
            }
            if data.scope == 'asset':
                template_data['title'] = data.title
            if data.action == 'create':
                row_indexes.set_description(f"Creating template {data[1]}")
                try:
                    template = self._create_template(template_data)
                    created_items.append(template)
                    self._update_sheet_row(ws, row_idx, template)
                    continue
                except Exception as e:
                    errors[row_idx] = [str(e)]
                    continue
            try:
                current = self._client.products[self._product_id].templates[data.id].get()
            except ClientError as e:
                if data.action == 'delete':
                    if e.status_code == 404:
                        deleted_items.append(data)
                        continue
                    errors[row_idx] = [str(e)]
                    continue
                errors[row_idx] = [
                    f'Cannot {data.action} template {data.id} since does not exist in the product.'
                    'Create it instead',
                ]
                continue
            if current['type'] != data.type or current['scope'] != data.scope:
                errors[row_idx] = [
                    f'Switching scope or type is not supported. '
                    f'Original scope {current["scope"]}, requested scope {data.scope}. '
                    f'Original type {current["type"]}, requested type {data.type}',
                ]
                continue
            try:
                if data.action == 'update':
                    template = self._update_template(data.id, template_data)
                    updated_items.append(template)
                    self._update_sheet_row(ws, row_idx, template)
                if data.action == 'delete':
                    self._client.products[self._product_id].templates[data.id].delete()
                    deleted_items.append(data)

            except Exception as e:
                errors[row_idx] = [str(e)]
        return (
            skipped_count,
            len(created_items),
            len(updated_items),
            len(deleted_items),
            errors,
        )

    def _create_template(self, template_data):
        return self._client.products[self._product_id].templates.create(template_data)

    def _update_template(self, tl_id, template_data):
        return self._client.products[self._product_id].templates[tl_id].update(template_data)

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
                f'Valid template types are `pending`, `fulfillment` or inquiring. Provided '
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
