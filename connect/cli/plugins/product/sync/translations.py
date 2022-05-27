# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from collections import namedtuple

from tqdm import tqdm

from connect.cli.plugins.product.constants import TRANSLATION_HEADERS
from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.cli.core.constants import DEFAULT_BAR_FORMAT


fields = (v.replace(' ', '_').lower() for v in TRANSLATION_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class TranslationsSynchronizer(ProductSynchronizer):
    def __init__(self, client, silent, stats):
        super().__init__(client, silent)
        self._mstats = stats['Translations']

    def sync(self):
        for row_idx, data in self._iterate_rows():
            self._set_process_description(f'Processing Product translation {data.translation_id}')
            if data.action == '-':
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue

    def _iterate_rows(self):
        self._progress = tqdm(
            enumerate(self._ws.iter_rows(min_row=2, values_only=True), 2),
            total=self._ws.max_row - 1, disable=self._silent, leave=True,
            bar_format=DEFAULT_BAR_FORMAT,
        )
        for row_idx, row in self._progress:
            yield row_idx, _RowData(*row)

    def _set_process_description(self, msg):
        self._progress.set_description(msg)

    @staticmethod
    def _validate_row(data):
        errors = []
        if data.action not in ('update', 'create', 'delete'):
            errors.append(
                f'Action must be `-`, `delete`, `update` or `create`. Provided {data.action}',
            )
            return errors

        if data.action == 'delete' and data.is_primary == 'Yes':
            errors.append('Can\'t delete the primary translation')

        if data.action in ('update', 'delete') and not data.translation_id:
            errors.append('Translation ID is required to update or delete a translation')

        if (
            data.action in ('update', 'create')
            and data.autotranslation not in ('Enabled', 'Disabled')
        ):
            errors.append(
                'Autotranslation must be `Enabled` or `Disabled`. '
                f'Provided {data.autotranslation}',
            )

        if data.action == 'create' and not data.locale:
            errors.append('Locale is required to create a translation')

        return errors
