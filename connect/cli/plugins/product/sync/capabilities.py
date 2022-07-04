from collections import namedtuple

from connect.cli.plugins.product.constants import CAPABILITIES
from connect.cli.plugins.shared.base import ProductSynchronizer
from connect.cli.plugins.shared.constants import CAPABILITIES_COLS_HEADERS
from connect.cli.plugins.product.utils import cleanup_product_for_update


fields = (v.replace(' ', '_').lower() for v in CAPABILITIES_COLS_HEADERS.values())

_RowData = namedtuple('RowData', fields)


class CapabilitiesSynchronizer(ProductSynchronizer):
    def __init__(self, client, progress, stats):
        super().__init__(client, progress)
        self._mstats = stats['Capabilities']

    def sync(self):  # noqa: CCR001
        ws = self._wb['Capabilities']

        task = self._progress.add_task('Processing Product capabilities', total=ws.max_row - 1)
        for row_idx in range(2, ws.max_row + 1):
            data = _RowData(*[ws.cell(row_idx, col_idx).value for col_idx in range(1, 4)])
            self._progress.update(
                task,
                description=f'Processing Product capabilities {data.capability}',
                advance=1,
            )
            if data.action == '-':
                self._mstats.skipped()
                continue
            row_errors = self._validate_row(data)

            if row_errors:
                self._mstats.error(row_errors, row_idx)
                continue

            product = cleanup_product_for_update(self._client.products[self._product_id].get())

            if data.action == 'update':
                update = True
                try:
                    if data.capability == 'Pay-as-you-go support and schema':
                        if data.value != 'Disabled':
                            if not product['capabilities'].get('ppu', False):
                                product['capabilities']['ppu'] = {
                                    'schema': data.value,
                                    'dynamic': False,
                                    'future': False,
                                }
                            else:
                                product['capabilities']['ppu']['schema'] = data.value
                        else:
                            product['capabilities']['ppu'] = None
                    if data.capability == 'Pay-as-you-go dynamic items support':
                        if not product['capabilities'].get('ppu', False):
                            if data.value == 'Enabled':
                                raise Exception(
                                    "Dynamic items support can't be enabled without Pay-as-you-go "
                                    "support",
                                )
                            update = False
                        else:
                            if data.value == 'Enabled':
                                product['capabilities']['ppu']['dynamic'] = True
                            else:
                                product['capabilities']['ppu']['dynamic'] = False
                    if data.capability == "Pay-as-you-go future charges support":
                        if not product['capabilities'].get('ppu', False):
                            if data.value == 'Enabled':
                                raise Exception(
                                    "Report of future charges can't be enabled without Pay-as-you-go "
                                    "support",
                                )
                            update = False

                        else:
                            if data.value == 'Enabled':
                                product['capabilities']['ppu']['future'] = True
                            else:
                                product['capabilities']['ppu']['future'] = False
                    if data.capability == 'Consumption reporting for Reservation Items':
                        if data.value == 'Enabled':
                            product['capabilities']['reservation']['consumption'] = True
                        else:
                            product['capabilities']['reservation']['consumption'] = False

                    if data.capability == 'Dynamic Validation of the Draft Requests':
                        if data.value == 'Enabled':
                            product['capabilities']['cart']['validation'] = True
                        else:
                            product['capabilities']['cart']['validation'] = False

                    if data.capability == 'Dynamic Validation of the Inquiring Form':
                        if data.value == 'Enabled':
                            product['capabilities']['inquiring']['validation'] = True
                        else:
                            product['capabilities']['inquiring']['validation'] = False

                    if data.capability == 'Reseller Authorization Level':
                        if data.value == 'Disabled':
                            product['capabilities']['tiers']['configs'] = None
                        else:
                            product['capabilities']['tiers']['configs'] = {
                                'level': data.value,
                            }
                    if data.capability == 'Tier Accounts Sync':
                        if data.value == 'Enabled':
                            product['capabilities']['tiers']['updates'] = True
                        else:
                            product['capabilities']['tiers']['updates'] = False
                    if data.capability == 'Administrative Hold':
                        if data.value == 'Enabled':
                            product['capabilities']['subscription']['hold'] = True
                        else:
                            product['capabilities']['subscription']['hold'] = False
                    if data.capability == 'Dynamic Validation of Tier Requests':
                        if data.value == 'Enabled':
                            product['capabilities']['tiers']['validation'] = True
                        else:
                            product['capabilities']['tiers']['validation'] = False
                    if data.capability == 'Editable Ordering Parameters in Change Request':
                        if data.value == 'Enabled':
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'editable_ordering_parameters'
                            ] = True
                        else:
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'editable_ordering_parameters'
                            ] = False
                    if data.capability == 'Validation of Draft Change Request':
                        if data.value == 'Enabled':
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'validation'
                            ] = True
                        else:
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'validation'
                            ] = False
                    if data.capability == 'Validation of inquiring form for Change Requests':
                        if data.value == 'Enabled':
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'inquiring_validation'
                            ] = True
                        else:
                            product[
                                'capabilities'
                            ][
                                'subscription'
                            ][
                                'change'
                            ][
                                'inquiring_validation'
                            ] = False
                    if update:
                        self._client.products[self._product_id].update(product)
                    self._mstats.updated()

                except Exception as e:
                    self._mstats.error(str(e), row_idx)
        self._progress.update(task, completed=ws.max_row - 1)

    @staticmethod
    def _validate_row(data):
        errors = []
        if data.capability not in CAPABILITIES:
            errors.append(
                f'Capability {data.capability} is not valid capability',
            )
        if data.capability == 'Pay-as-you-go support and schema':
            if data.value not in (
                'Disabled', 'QT', 'TR', 'PR', 'CR',
            ):
                errors.append(f'Schema {data.value} is not supported')
            return errors
        if data.capability == 'Reseller Authorization Level' and data.value not in (
            'Disabled', 1, 2,
        ):
            errors.append(f'{data.value } is not valid for Reseller Authorization level capability')
            return errors
        if (
            data.value not in ('Disabled', 'Enabled')
            and data.capability != 'Reseller Authorization Level'
        ):
            errors.append(f'{data.capability} may be Enabled or Disabled, but not {data.value}')
        return errors
