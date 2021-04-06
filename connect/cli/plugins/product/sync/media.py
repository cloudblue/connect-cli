# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2021 Ingram Micro. All Rights Reserved.
import os
from collections import namedtuple
from urllib.parse import urlparse

from tqdm import trange
from requests_toolbelt.multipart.encoder import MultipartEncoder

from connect.cli.core.constants import DEFAULT_BAR_FORMAT
from connect.cli.plugins.product.constants import MEDIA_COLS_HEADERS
from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.client import ClientError


fields = (v.replace(' ', '_').lower() for v in MEDIA_COLS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class MediaSynchronizer(ProductSynchronizer):
    def __init__(self, client, silent):
        self._media_path = None
        super(MediaSynchronizer, self).__init__(client, silent)

    def open(self, input_file, worksheet):
        self._media_path = input_file.rsplit('/', 1)[0]
        return super(MediaSynchronizer, self).open(input_file, worksheet)

    def sync(self):  # noqa: CCR001
        ws = self._wb['Media']
        errors = {}
        skipped_count = 0
        created_items = []
        updated_items = []
        deleted_items = []

        row_indexes = trange(
            2, ws.max_row + 1, disable=self._silent, leave=True, bar_format=DEFAULT_BAR_FORMAT,
        )
        for row_idx in row_indexes:
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 7)])
            row_indexes.set_description(f'Processing Media {data.id or data.position or "New"}')

            if data.action == '-':
                skipped_count += 1
                continue
            row_errors = self._validate_row(data)

            if row_errors:
                errors[row_idx] = row_errors
                continue
            if data.action == 'delete':
                try:
                    self._client.products[self._product_id].media[data.id].delete()
                    deleted_items.append(data)
                    continue
                except ClientError as e:
                    if e.status_code == 404:
                        deleted_items.append(data)
                    else:
                        errors[row_idx] = [str(e)]
                    continue
            if data.type == 'image':
                payload = MultipartEncoder(
                    fields={
                        'type': (data.type, data.type),
                        'position': (str(data.position), str(data.position)),
                        'thumbnail': (
                            data.image_file,
                            open(
                                os.path.join(
                                    self._media_path,
                                    'media',
                                    data.image_file,
                                ),
                                "rb",
                            ),
                        ),
                    },
                )
            else:
                payload = MultipartEncoder(
                    fields={
                        'type': (data.type, data.type),
                        'position': (str(data.position), str(data.position)),
                        'thumbnail': (
                            data.image_file,
                            open(
                                os.path.join(
                                    self._media_path,
                                    'media',
                                    data.image_file,
                                ),
                                "rb",
                            ),
                        ),
                        'url': data.video_url_location,
                    },
                )
            try:
                if data.action == 'update':
                    media = self._client.products[self._product_id].media[data.id].update(
                        data=payload,
                        headers={'Content-Type': payload.content_type},
                    )
                    self._update_sheet_row(ws, row_idx, media)
                    updated_items.append(media)
                else:
                    media = self._client.products[self._product_id].media.create(
                        data=payload,
                        headers={'Content-Type': payload.content_type},
                    )
                    self._update_sheet_row(ws, row_idx, media)
                    created_items.append(media)
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
