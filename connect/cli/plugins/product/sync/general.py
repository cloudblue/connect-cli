import os

from click import ClickException
from requests_toolbelt.multipart.encoder import MultipartEncoder

from connect.cli.plugins.product.sync.base import ProductSynchronizer
from connect.cli.plugins.product.utils import cleanup_product_for_update
from connect.client import ClientError


class GeneralSynchronizer(ProductSynchronizer):
    def __init__(self, client, silent):
        self._category = None
        self._media_path = None
        super(GeneralSynchronizer, self).__init__(client, silent)

    def open(self, input_file, worksheet):
        self._open_workbook(input_file)
        self._media_path = input_file.rsplit('/', 1)[0]
        if worksheet not in self._wb.sheetnames:
            raise ClickException(f'File does not contain {worksheet} to synchronize')
        ws = self._wb['General Information']
        if ws['A5'] and ws['A5'].value != 'Product ID' or not ws['B5']:
            raise ClickException(
                'Input file has invalid format and could not read product id from it',
            )
        product_id = ws['B5'].value
        if not self._client.products[product_id].exists():
            raise ClickException(f'Product {product_id} not found, create it first.')
        errors = self._validate_general(ws)
        if errors:
            raise ClickException(
                f'Errors has been detected on General Information tab: {".".join(errors)}',
            )
        self._product_id = product_id
        return self._product_id

    def _validate_general(self, ws):  # noqa: CCR001
        errors = []
        if ws['A8'].value != 'Product Category':
            errors.append(
                'A8 must be `Product Category` and B8 contain the value',
            )
            return errors
        if not self._assign_cat_id(ws['B8'].value):
            errors.append(
                f'Product category {ws["B8"].value} is a not known category',
            )
        if ws['A9'] and ws['A9'].value != 'Product Icon file name':
            errors.append(
                'A9 must be `Product Icon file name` and B9 contain the value',
            )
        if (ws['B9'] and ws['B9'].value) and not os.path.isfile(
                os.path.join(
                    self._media_path,
                    'media',
                    ws['B9'].value,
                ),
        ):
            errors.append(
                f'File {ws["B9"].value} does not exist in the media folder',
            )
        if (
            (ws['A10'] and ws['A10'].value != 'Product Short Description')
            or len(ws['B10'].value) > 512
        ):
            errors.append(
                'Short description is mandatory and must be on B10, short description can not '
                'exceed 512 characters',
            )
        if ws['A11'] and ws['A11'].value != 'Product Detailed Description':
            errors.append(
                'Product detailed description is required',
            )
        if ws['A12'] and ws['A12'].value != 'Embedding description':
            errors.append(
                'Embedding description is required',
            )
        if ws['A13'] and ws['A13'].value != 'Embedding getting started':
            errors.append(
                'Embedding getting started is required',
            )
        return errors

    def _assign_cat_id(self, category_name):
        categories = self._client.categories.all()
        for category in categories:
            if category['name'] == category_name:
                self._category = category['id']
                return category['id']

    def sync(self):
        errors = []
        product = cleanup_product_for_update(self._client.products[self._product_id].get())
        ws = self._wb['General Information']
        product['short_description'] = ws['B10'].value.replace('\n', '')
        product['detailed_description'] = ws['B11'].value
        product['customer_ui_settings']['description'] = ws['B12'].value
        product['customer_ui_settings']['getting_started'] = ws['B12'].value
        product['name'] = ws['B6'].value
        product['category']['name'] = ws['B8'].value
        product['category']['id'] = self._category
        # Solution for v22 to avoid issue while updating capabilities
        del product['capabilities']['subscription']['change']['editable_ordering_parameters']
        try:
            self._client.products[self._product_id].update(product)
        except ClientError as e:
            errors.append(
                f'Error while updating general product information: {str(e)}',
            )
            return errors
        payload = MultipartEncoder(
            fields={
                'icon': (
                    ws['B9'].value,
                    open(
                        os.path.join(
                            self._media_path,
                            'media',
                            ws['B9'].value,
                        ),
                        "rb",
                    ),
                ),
            },
        )
        try:
            self._client.products[self._product_id].update(
                data=payload,
                headers={'Content-Type': payload.content_type},
            )
        except ClientError as e:
            errors.append(
                f'Error while updating general product information: {str(e)}',
            )

        return errors
