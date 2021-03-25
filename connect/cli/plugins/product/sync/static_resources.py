from collections import namedtuple
from urllib.parse import urlparse

from tqdm import trange

from connect.cli.core.constants import DEFAULT_BAR_FORMAT
from connect.cli.plugins.product.constants import STATIC_LINK_HEADERS
from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.cli.plugins.product.utils import cleanup_product_for_update


fields = (v.replace(' ', '_').lower() for v in STATIC_LINK_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class StaticResourcesSynchronizer(ProductSynchronizer):
    def sync(self):  # noqa: CCR001
        ws = self._wb['Embedding Static Resources']
        errors = {}
        skipped_count = 0
        created_items = []
        deleted_items = []

        row_indexes = trange(
            2, ws.max_row + 1, disable=self._silent, leave=True, bar_format=DEFAULT_BAR_FORMAT,
        )
        download = []
        documentation = []
        for row_idx in row_indexes:
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 5)])
            row_indexes.set_description(f'Processing item {data.title or data.type}')
            if data.action not in ('-', 'create', 'delete'):
                skipped_count += 1
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                errors[row_idx] = row_errors
                continue
            if data.action == 'delete':
                deleted_items.append(data.title)
                continue
            if data.type == 'Download':
                download.append(
                    {
                        "title": data.title,
                        "url": data.url,
                        "visible_for": "admin",
                    },
                )
            if data.type == "Documentation":
                documentation.append(
                    {
                        "title": data.title,
                        "url": data.url,
                    },
                )
            if data.action == '-':
                skipped_count += 1
            else:
                created_items.append(data.title)

        product = cleanup_product_for_update(self._client.products[self._product_id].get())
        try:
            product['customer_ui_settings']['download_links'] = download
            product['customer_ui_settings']['documents'] = documentation
            self._client.products[self._product_id].update(product)
        except Exception as e:
            errors[1] = [str(e)]

        return (
            skipped_count,
            len(created_items),
            len(deleted_items),
            errors,
        )

    @staticmethod
    def _validate_row(data):
        errors = []

        if data.type not in ('Download', 'Documentation'):
            errors.append(
                f'Static resource of type {data.type} is not known, must be either Download or '
                f'Documentation type.',
            )
        if not data.title:
            errors.append(
                'Title is required',
            )
        if not data.url:
            errors.append(
                'Url is mandatory for create or delete actions',
            )
            return errors
        result = urlparse(data.url)
        if result.scheme not in ('http', 'https'):
            errors.append(
                f'Url provided has invalid protocol, url must be http or https type, provided '
                f'{result.scheme}.',
            )
        if not result.netloc:
            errors.append(
                'Url provided seems to be invalid, please validate it.',
            )
        return errors
