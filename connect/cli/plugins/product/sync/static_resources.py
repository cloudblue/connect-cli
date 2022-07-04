from collections import namedtuple
from urllib.parse import urlparse

from connect.cli.plugins.shared.constants import STATIC_LINK_HEADERS
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.product.utils import cleanup_product_for_update


fields = (v.replace(' ', '_').lower() for v in STATIC_LINK_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class StaticResourcesSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        super().__init__(client, progress)
        self._mstats = stats['Static Resources']

    def sync(self):  # noqa: CCR001
        ws = self._wb['Embedding Static Resources']

        task = self._progress.add_task('Processing item', total=ws.max_row - 1)

        download = []
        documentation = []
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 5)])
            self._progress.update(
                task,
                description=f'Processing item {data.title or data.type}',
                advance=1,
            )
            if data.action not in ('-', 'create', 'delete'):
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)
            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue
            if data.action == 'delete':
                self._mstats.deleted()
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
                self._mstats.skipped()
            else:
                self._mstats.created()

        self._progress.update(task, completed=ws.max_row - 1)
        product = cleanup_product_for_update(self._client.products[self._product_id].get())
        try:
            product['customer_ui_settings']['download_links'] = download
            product['customer_ui_settings']['documents'] = documentation
            self._client.products[self._product_id].update(product)
        except Exception as e:
            self._mstats.error(str(e), 1)

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
