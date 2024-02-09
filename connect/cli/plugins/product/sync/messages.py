# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2024 Ingram Micro. All Rights Reserved.

from collections import namedtuple

from connect.client.rql import R
from connect.client import ClientError, R

from connect.cli.core.http import handle_http_error
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.shared.constants import MESSAGES_HEADERS


fields = (v.replace(' ', '_').lower() for v in MESSAGES_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class MessageSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        self._mstats = stats['Messages']
        super().__init__(client, progress)

    def _get_message(self, message_id):
        try:
            res = self._client.products[self._product_id].messages[message_id].get()
        except ClientError as error:
            if error.status_code == 404:
                return
            handle_http_error(error)
        return res

    def _create_message(self, data):
        try:
            payload = {'external_id': data.external_id, 'value': data.value, 'auto': data.auto}
            res = self._client.products[self._product_id].messages.create(payload)
        except ClientError as error:
            handle_http_error(error)
        return res

    def _update_message(self, data):
        try:
            payload = {'external_id': data.external_id, 'value': data.value, 'auto': data.auto}
            res = self._client.products[self._product_id].messages[data.id].update(payload)
        except ClientError as error:
            handle_http_error(error)
        return res

    def _delete_message(self, message_id):
        try:
            res = self._client.products[self._product_id].messages[message_id].delete()
        except ClientError as error:
            handle_http_error(error)
        return res

    def _process_create(self, row_idx, data, task):
        rql = R().external_id.eq(data.external_id)
        message = self._client.products[self._product_id].messages.filter(rql).first()
        if message:
            self._mstats.error(
                f'Cannot create message: message with external_id `{data.external_id}`'
                f' already exists with ID `{message["id"]}`.',
                row_idx,
            )
        else:
            self._progress.update(
                task,
                description=f'Creating message {data.external_id}',
            )
            try:
                new_message = self._create_message(data)
                self._mstats.created()
                self._update_sheet_row(self._ws, row_idx, new_message)
            except Exception as e:
                self._mstats.error(str(e), row_idx)

    def _process_update(self, row_idx, data, task):
        if not self._get_message(data.id):
            self._mstats.error(
                f'Cannot update message: message with ID `{data.id}` ' 'does not exist.',
                row_idx,
            )
        else:
            self._progress.update(
                task,
                description=f'Updating message {data.id}',
            )
            try:
                updated_message = self._update_message(
                    data,
                )
                self._mstats.updated()
                self._update_sheet_row(self._ws, row_idx, updated_message)
            except Exception as e:
                self._mstats.error(str(e), row_idx)

    def _process_delete(self, row_idx, data, task):
        if not self._get_message(data.id):
            self._mstats.error(
                f'Cannot delete message: message with ID `{data.id}` ' 'does not exist.',
                row_idx,
            )
        else:
            self._progress.update(
                task,
                description=f'Deleting message {data.id}',
            )
            try:
                self._delete_message(data.id)
                self._mstats.deleted()
                for c in range(1, self._ws.max_column + 1):
                    self._ws.cell(row_idx, c, value='')
            except Exception as e:
                self._mstats.error(str(e), row_idx)

    def sync(self):  # noqa: CCR001
        self._ws = self._wb['Messages']
        task = self._progress.add_task('Processing messages', total=self._ws.max_row - 1)
        for row_idx in range(2, self._ws.max_row + 1):
            data = _RowData(*[self._ws.cell(row_idx, col_idx).value for col_idx in range(1, 6)])
            self._progress.update(
                task,
                description=f'Processing message {data.id}',
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
                self._process_create(row_idx, data, task)
            elif data.action == 'update':
                self._process_update(row_idx, data, task)
            elif data.action == 'delete':
                self._process_delete(row_idx, data, task)

        self._progress.update(task, completed=self._ws.max_row - 1)

    def _validate_row(self, row):  # noqa: CCR001
        errors = []

        if row.action == 'create' and row.id:
            errors.append(
                'the `ID` must not be specified for the `create` action.',
            )
            return errors
        if row.action in ('update', 'delete') and not row.id:
            errors.append(
                'the `ID` must be specified for the `update` or `delete` actions.',
            )
            return errors
        if (
            row.action in ('create', 'update', 'delete')
            and row.external_id is None
            or row.value is None
        ):
            errors.append(
                'the `External ID` and `Value` must be specified for the `create`, `update` or `delete` actions.',
            )
            return errors

    @staticmethod
    def _update_sheet_row(ws, row_idx, message):
        ws.cell(row_idx, 1, value=message['id'])
        ws.cell(row_idx, 2, value='-')
        ws.cell(row_idx, 3, value=message['external_id'])
        ws.cell(row_idx, 4, value=message['value'])
        ws.cell(row_idx, 5, value=message['auto'])
