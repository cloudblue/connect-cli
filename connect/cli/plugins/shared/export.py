from copy import copy
from io import BytesIO

from click import ClickException
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.filters import AutoFilter
from openpyxl.utils import get_column_letter

from connect.client import ClientError, ConnectClient
from connect.client.utils import get_headers
from connect.cli.core.http import format_http_status, handle_http_error
from connect.cli.plugins.translation.utils import insert_column_ws, logged_request

EXCEL_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _get_translation_workbook(api_url, api_key, translation_id, verbose=False):
    try:
        client = ConnectClient(api_key=api_key, endpoint=api_url, use_specs=False)
        attributes_path = client.ns('localization').translations[translation_id].attributes.path
        url = f'{api_url}/{attributes_path}'
        response = logged_request('GET', url, verbose, headers={
            'Content-type': EXCEL_CONTENT_TYPE, **get_headers(api_key),
        })
        if response.status_code != 200:
            raise ClientError(status_code=response.status_code)
        return load_workbook(filename=BytesIO(response.content))
    except ClientError as error:
        if error.status_code == 404:
            status = format_http_status(error.status_code)
            raise ClickException(f'{status}: Translation {translation_id} not found.')
        handle_http_error(error)


def _alter_attributes_sheet(ws):
    # Search for the 'value' column
    for col_idx in range(1, ws.max_column + 1):
        if ws.cell(1, col_idx).value.lower() == 'value':
            new_column = col_idx
            break
    else:
        return

    # Add new 'action' column before 'value' column
    fill = copy(ws.cell(1, 1).fill)
    font = copy(ws.cell(1, 1).font)
    insert_column_ws(ws, new_column, 20)
    header_cell = ws.cell(1, new_column)
    header_cell.value = 'action'
    header_cell.fill = fill
    header_cell.font = font

    # Setup 'action' column cells
    if ws.max_row > 1:
        action_validation = DataValidation(type='list', formula1='"-,update"', allow_blank=False)
        ws.add_data_validation(action_validation)
        for row_idx in range(2, ws.max_row + 1):
            cell = ws.cell(row_idx, new_column)
            cell.alignment = Alignment(vertical='top')
            cell.value = '-'
            action_validation.add(cell)

    # (re)set auto filter
    ws.auto_filter = AutoFilter(ref=f'A:{get_column_letter(ws.max_column)}')
    for col_idx in range(1, ws.max_column + 1):
        ws.auto_filter.add_filter_column(col_idx, [], blank=False)
