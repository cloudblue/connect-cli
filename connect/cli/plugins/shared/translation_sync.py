# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from collections import defaultdict, namedtuple
from functools import partial

from connect.cli.plugins.shared.constants import TRANSLATION_HEADERS
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.shared.utils import fill_translation_row, setup_locale_data_validation
from connect.client import ClientError

fields = (v.replace(' ', '_').lower() for v in TRANSLATION_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class TranslationsSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        super().__init__(client, progress)
        self._mstats = stats['Translations']
        self._translations_autotranslating = []
        self._new_translations = []

    @property
    def translations_autotranslating(self):
        """
        After a call to sync(), this is a list of translation IDs that potentially could have an
        auto-translation task running.
        """
        return self._translations_autotranslating

    @property
    def new_translations(self):
        return self._new_translations

    def sync(self):
        rows_data = defaultdict(dict)
        for row_idx, data in self._iterate_rows():
            self._set_process_description(f'Processing Product translation {data.translation_id or data.locale}')
            if data.action == '-' or data.is_primary == 'Yes':
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue
            rows_data[data.action][row_idx] = data
        self._process_rows_data(rows_data)
        self._progress.update(self._task, completed=self._ws.max_row - 1)

    def save(self, output_file):
        setup_locale_data_validation(self._wb['General Information'], self._ws)
        super().save(output_file)

    def _iterate_rows(self):
        self._task = self._progress.add_task(
            'Processing Product translation',
            total=self._ws.max_row - 1,
        )
        for row_idx, row in enumerate(self._ws.iter_rows(min_row=2, values_only=True), 2):
            self._progress.update(self._task, advance=1)
            yield row_idx, _RowData(*row)

    def _set_process_description(self, msg):
        self._progress.update(self._task, description=msg)

    @staticmethod
    def _validate_row(data):
        errors = []
        if data.action not in ('update', 'create', 'delete'):
            errors.append(
                f'Action must be `-`, `delete`, `update` or `create`. Provided {data.action}',
            )
            return errors

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

    def _process_rows_data(self, rows_data):
        self._translations_autotranslating = []
        # for a consistent sync first delete translations, then update and create
        for row_idx, data in rows_data['delete'].items():
            self._handle_action(self._action_delete, row_idx, data)

        for row_idx, data in rows_data['update'].items():
            self._handle_action(self._action_update, row_idx, data)

        if len(rows_data['create']) > 0:
            # if there are any translations to create, then the context_id is needed
            try:
                ctx = self._client.ns('localization').contexts.filter(
                    instance_id=self._product_id,
                ).first()
                for row_idx, data in rows_data['create'].items():
                    self._handle_action(partial(self._action_create, ctx['id']), row_idx, data)
            except ClientError as e:
                self._mstats.error(str(e).split('\n'))

    def _handle_action(self, action_handler, row_idx, data):
        try:
            translation = action_handler(data)
            if translation:
                fill_translation_row(self._ws, row_idx, translation, update_mode=True)
        except Exception as e:
            self._mstats.error(str(e).split('\n'), row_idx)

    def _action_delete(self, data):
        self._set_process_description(f'Deleting translation {data.translation_id}')
        try:
            self._client.ns('localization').translations[data.translation_id].delete()
        except ClientError as e:
            if e.status_code != 404:
                raise
        self._mstats.deleted()

    def _action_update(self, data):
        self._set_process_description(f'Updating translation {data.translation_id}')
        payload = {
            'description': data.description or "",
            'auto': {
                'enabled': data.autotranslation == 'Enabled',
            },
        }
        translation = self._client.ns('localization').translations[data.translation_id].update(payload)
        self._mstats.updated()
        if translation['auto']['enabled']:
            self._translations_autotranslating.append(translation['id'])
        return translation

    def _action_create(self, context_id, data):
        self._set_process_description('Creating new translation')
        payload = {
            'context': {'id': context_id},
            "locale": {'id': data.locale.split()[0]},
            'description': data.description or "",
            'auto': {
                'enabled': data.autotranslation == 'Enabled',
            },
        }
        translation = self._client.ns('localization').translations.create(payload)
        self._new_translations.append(translation)
        self._mstats.created()
        if translation['auto']['enabled']:
            self._translations_autotranslating.append(translation['id'])
        return translation
