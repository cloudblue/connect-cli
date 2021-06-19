from datetime import datetime

from click import ClickException, echo as clickecho
from fs.tempfs import TempFS
from openpyxl import load_workbook

from connect.cli.plugins.product.export import dump_product
from connect.cli.plugins.product.sync import (
    ActionsSynchronizer,
    CapabilitiesSynchronizer,
    GeneralSynchronizer,
    ItemSynchronizer,
    MediaSynchronizer,
    ParamsSynchronizer,
    TemplatesSynchronizer,
)
from connect.client import ClientError, ConnectClient, RequestLogger


class ProductCloner:
    def __init__(self, config, source_account, destination_account, product_id):
        self.fs = TempFS(identifier=f'_clone_{product_id}')
        self.config = config
        self.source_account = (source_account if source_account else config.active.id)
        self.destination_account = (destination_account if destination_account else config.active.id)
        self.product_id = product_id
        self.destination_product = None
        self.wb = None

    def dump(self):
        dump_product(
            api_url=self.config.active.endpoint,
            api_key=self.config.active.api_key,
            product_id=self.product_id,
            output_path=self.fs.root_path,
            output_file='',
            silent=self.config.silent,
            verbose=self.config.verbose,
        )

    def inject(self):  # noqa: CCR001
        try:
            self.config.activate(self.destination_account)
            input_file = f'{self.fs.root_path}/{self.product_id}/{self.product_id}.xlsx'
            client = ConnectClient(
                api_key=self.config.active.api_key,
                endpoint=self.config.active.endpoint,
                use_specs=False,
                max_retries=3,
                logger=RequestLogger() if self.config.verbose else None,
            )
            synchronizer = GeneralSynchronizer(
                client,
                self.config.silent,
            )

            synchronizer.open(input_file, 'General Information')
            synchronizer.sync()
            clickecho('\n')
            synchronizer = ItemSynchronizer(
                client,
                self.config.silent,
            )
            product_id = synchronizer.open(input_file, 'Items')
            items = client.products[product_id].items.all()
            for item in items:
                client.products[product_id].items[item['id']].delete()
            synchronizer.sync()
            clickecho('\n')
            synchronizer = CapabilitiesSynchronizer(
                client,
                self.config.silent,
            )
            synchronizer.open(input_file, 'Capabilities')
            synchronizer.sync()
            clickecho('\n')
            templates = client.products[product_id].templates.all()
            sample_templates = []
            for template in templates:
                sample_templates.append(template['id'])

            synchronizer = TemplatesSynchronizer(
                client,
                self.config.silent,
            )

            synchronizer.open(input_file, 'Templates')
            synchronizer.sync()

            for template in sample_templates:
                try:
                    client.products[product_id].templates[template].delete()
                except ClientError:
                    # done intentionally till fulfillment in progress template not on public api
                    pass

            clickecho('\n')
            synchronizer = ParamsSynchronizer(
                client,
                self.config.silent,
            )

            synchronizer.open(input_file, "Ordering Parameters")
            synchronizer.sync()
            clickecho('\n')
            synchronizer.open(input_file, "Fulfillment Parameters")
            synchronizer.sync()
            clickecho('\n')
            synchronizer.open(input_file, "Configuration Parameters")
            synchronizer.sync()
            clickecho('\n')

            synchronizer = ActionsSynchronizer(
                client,
                self.config.silent,
            )

            synchronizer.open(input_file, 'Actions')
            synchronizer.sync()
            clickecho('\n')

            synchronizer = MediaSynchronizer(
                client,
                self.config.silent,
            )

            synchronizer.open(input_file, 'Media')
            synchronizer.sync()
            clickecho('\n')

            self.config.activate(self.source_account)
        except ClientError as e:
            raise ClickException(f"Error while cloning product: {str(e)}")

    def load_wb(self):
        self.wb = load_workbook(
            f'{self.fs.root_path}/{self.product_id}/{self.product_id}.xlsx',
            data_only=True,
        )

    def create_product(self, name=None):
        if not name:
            time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            name = f"Clone of {self.product_id} {time}"
        ws = self.wb['General Information']
        ws['B6'].value = name
        self.config.activate(self.destination_account)

        try:
            client = ConnectClient(
                api_key=self.config.active.api_key,
                endpoint=self.config.active.endpoint,
                use_specs=False,
                max_retries=3,
                logger=RequestLogger() if self.config.verbose else None,
            )
            category = self._get_cat_id(client, ws['B8'].value)
            product = client.products.create(
                {
                    "name": name,
                    "category": {
                        "id": category,
                    },
                },
            )
            if name:
                ws['B6'].value = name
            ws['B5'].value = product['id']
            self.destination_product = product['id']
            self.wb.save(f'{self.fs.root_path}/{self.product_id}/{self.product_id}.xlsx')
        except ClientError as e:
            raise ClickException(f'Error on product creation: {str(e)}')

    def clean_wb(self):
        ws = self.wb['Capabilities']
        for row in range(2, 11):
            ws[f'B{row}'].value = 'update'

        ws = self.wb['Embedding Static Resources']
        for row in range(2, ws.max_row + 1):
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Media']
        for row in range(2, ws.max_row + 1):
            ws[f'B{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Templates']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Items']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Ordering Parameters']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Fulfillment Parameters']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Configuration Parameters']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'

        ws = self.wb['Actions']
        for row in range(2, ws.max_row + 1):
            ws[f'A{row}'].value = ''
            ws[f'C{row}'].value = 'create'
        self.wb.save(f'{self.fs.root_path}/{self.product_id}/{self.product_id}.xlsx')

    @staticmethod
    def _get_cat_id(client, category_name):
        categories = client.categories.all()
        for category in categories:
            if category['name'] == category_name:
                return category['id']
