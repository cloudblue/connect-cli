from cnctcli.actions.products.sync import ProductSynchronizer
from click import ClickException


class GeneralSynchronizer(ProductSynchronizer):
    def open(self, input_file, worksheet):
        self._open_workbook(input_file)
        if worksheet not in self._wb.sheetnames:
            raise ClickException(f'File does not contain {worksheet} to synchronize')
        ws = self._wb['General Information']
        if ws['A5'].value != 'Product ID':
            raise ClickException(
                'Input file has invalid format and could not read product id from it'
            )
        product_id = ws['B5'].value
        if not self._client.products[product_id].exists():
            raise ClickException(f'Product {product_id} not found, create it first.')
        self._product_id = product_id
        return self._product_id
