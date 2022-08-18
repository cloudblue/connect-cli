# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import os
from collections import namedtuple
from urllib.parse import urlparse
import json
from mimetypes import guess_type

from connect.cli.plugins.shared.constants import MEDIA_COLS_HEADERS
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.client import ClientError


fields = (v.replace(' ', '_').lower() for v in MEDIA_COLS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class MediaSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        self._media_path = None
        self._mstats = stats['Media']
        super(MediaSynchronizer, self).__init__(client, progress)

    def open(self, input_file, worksheet):
        self._media_path = input_file.rsplit('/', 1)[0]
        return super(MediaSynchronizer, self).open(input_file, worksheet)

    def sync(self):  # noqa: CCR001
        ws = self._wb['Media']

        task = self._progress.add_task('Processing Media', total=ws.max_row - 1)
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 7)])
            self._progress.update(
                task,
                description=f'Processing Media {data.id or data.position or "New"}',
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
                    self._client.products[self._product_id].media[data.id].delete()
                    self._mstats.deleted()
                    continue
                except ClientError as e:
                    if e.status_code == 404:
                        self._mstats.deleted()
                    else:
                        self._mstats.error(str(e), row_idx)
                    continue

            image_data = open(
                os.path.join(
                    self._media_path,
                    'media',
                    data.image_file,
                ),
                "rb",
            )
            image_type, _ = guess_type(data.image_file)
            body = {
                'type': data.type,
                'position': str(data.position),
            }

            if data.type != 'image':
                body['url'] = data.video_url_location

            payload = {
                'body': (None, json.dumps(body), 'application/json'),
                'thumbnail': (data.image_file, image_data, image_type),
            }

            try:
                if data.action == 'update':
                    media = self._client.products[self._product_id].media[data.id].update(
                        files=payload,
                    )
                    self._update_sheet_row(ws, row_idx, media)
                    self._mstats.updated()
                else:
                    media = self._client.products[self._product_id].media.create(
                        files=payload,
                    )
                    self._update_sheet_row(ws, row_idx, media)
                    self._mstats.created()
            except Exception as e:
                self._mstats.error(str(e), row_idx)
        self._progress.update(task, completed=ws.max_row - 1)

    @staticmethod
    def _update_sheet_row(ws, row_idx, media):
        ws.cell(row_idx, 1, value=media['position'])
        ws.cell(row_idx, 2, value=media['id'])

    def _validate_row(self, data):
        errors = []
        if not data.position or not str(data.position).isdigit() or int(data.position) > 8:
            errors.append("Position is required and must be an integer between 1 and 8")
        elif data.action != 'create' and not data.id.startswith('PRDM-'):
            errors.append('ID does not seam to be valid.')
        elif not data.image_file:
            errors.append("Image file is required")
        elif data.action not in ('-', 'create', 'update', 'delete'):
            errors.append(
                f'Supported actions are `-`, `create`, `update` or `delete`. Provided {data.action}',
            )
        elif not data.type or data.type not in ('image', 'video'):
            errors.append(
                f'Media can be either image or video type, provided {data.type}',
            )
        elif not os.path.isfile(os.path.join(self._media_path, 'media', data.image_file)):
            errors.append(
                f'Image file is not found, please check that file {data.image_file} exists '
                'in media folder',
            )
        elif data.type == 'video' and (not data.video_url_location):
            errors.append(
                'Video URL location is required for video type',
            )
        elif data.type == 'video' and not self.is_valid_video_url(data.video_url_location):
            errors.append(
                'Videos can be hosted on youtube or vimeo, please also ensure to provide https url.'
                f' Invalid url provided is {data.video_url_location}',
            )

        return errors

    @staticmethod
    def is_valid_video_url(location):
        url = urlparse(location)
        if url.scheme != 'https' or url.netloc not in (
            'www.vimeo.com',
            'vimeo.com',
            'youtube.com',
            'www.youtube.com',
            'www.youtu.be',
            'youtu.be',
        ):
            return False
        return True
