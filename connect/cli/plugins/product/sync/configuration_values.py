import json
import re
from collections import namedtuple

from tqdm import trange

from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.cli.plugins.product.constants import (
    CONFIGURATION_HEADERS,
)
from connect.cli.core.constants import DEFAULT_BAR_FORMAT


fields = (v.replace(' ', '_').lower() for v in CONFIGURATION_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class ConfigurationValuesSynchronizer(ProductSynchronizer):

    def sync(self):  # noqa: CCR001
        ws = self._wb['Configuration']
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
            row_indexes.set_description(f'Processing Configuration value {data.id}')
            if data.action == '-':
                skipped_count += 1
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                errors[row_idx] = row_errors
                continue

            scope_calc = data.id.split('#')
            payload = {
                'parameter': {
                    'id': scope_calc[0],
                },
            }
            if scope_calc[1]:
                payload['item'] = {
                    'id': scope_calc[1],
                }
            if scope_calc[2]:
                payload['marketplace'] = {
                    'id': scope_calc[2],
                }

            if data.action == 'update':
                try:
                    value = json.loads(data.value)
                    payload['structured_value'] = value
                except Exception:
                    payload['value'] = str(data.value)

            try:
                self._client.products[self._product_id].configurations.create(payload)
                if data.action == 'delete':
                    deleted_items.append(data)
                else:
                    updated_items.append(data)
            except Exception as e:
                errors[row_idx] = [str(e)]

        return (
            skipped_count,
            len(created_items),
            len(updated_items),
            len(deleted_items),
            errors,
        )

    @staticmethod
    def _validate_row(data):
        errors = []

        if not data.id:
            errors.append(
                'ID is required for update operation',
            )
        elif data.id.count('#') != 2:
            errors.append(
                'ID is not properly formatted',
            )
        if errors:
            return errors
        if data.action == 'update' and (not data.value or data.value == '-'):
            errors.append(
                'Value is required for update operation',
            )
        id_pattern = "^[A-Za-z0-9_#-]*$"

        if not bool(re.match(id_pattern, data.id)):
            errors.append(
                'ID is not properly formatted',
            )
            return errors
        if data.action not in ('-', 'update', 'delete'):
            errors.append(
                f'Action can be either `-` or `update`, provided {data.action}',
            )
            return errors
        scope_calc = data.id.split('#')
        if scope_calc[0] and scope_calc[0] != data.parameter:
            errors.append(
                'Parameter does not match configuration ID',
            )
        if scope_calc[1] and scope_calc[1] != data.item_id:
            errors.append(
                'Item does not match configuration ID',
            )
        if scope_calc[2] and scope_calc[2] != data.marketplace_id:
            errors.append(
                'Marketplace does not match configuration ID',
            )
        if errors:
            return errors
