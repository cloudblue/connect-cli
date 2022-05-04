# -*- coding: utf-8 -*-

# This file is part of the Ingram Micro Cloud Blue Connect connect-cli.
# Copyright (c) 2019-2022 Ingram Micro. All Rights Reserved.

from click import ClickException
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.styles.colors import Color, WHITE
from openpyxl.worksheet.datavalidation import DataValidation

from connect.client import ClientError, ConnectClient, RequestLogger
from connect.cli.core.http import (
    format_http_status,
    handle_http_error,
)
from connect.cli.plugins.translation.export_attributes import dump_translation_attributes
from connect.cli.core.utils import validate_output_options


def dump_translation(
    api_url, api_key, translation_id, output_file,
    silent, verbose=False, output_path=None,
):
    output_file = validate_output_options(output_path, output_file, default_dir_name=translation_id)
    try:
        client = ConnectClient(
            api_key=api_key,
            endpoint=api_url,
            use_specs=False,
            max_retries=3,
            logger=RequestLogger() if verbose else None,
        )
        translation = client.ns('localization').translations[translation_id].get()
        wb = Workbook()
        _dump_general(wb.active, translation)
        dump_translation_attributes(wb.create_sheet('Attributes'), client, translation_id, silent)
        wb.save(output_file)
    except ClientError as error:
        if error.status_code == 404:
            status = format_http_status(error.status_code)
            raise ClickException(f'{status}: Translation {translation_id} not found.')
        handle_http_error(error)

    return output_file


def _dump_general(ws, translation):
    _set_ws_main_header(ws, 'Translation information')
    ws.title = 'General'
    for row_idx in range(3, 10):
        for col_idx in [1, 2]:
            ws.cell(row_idx, col_idx).font = Font(sz=12)
    disabled_enabled = DataValidation(
        type='list',
        formula1='"Disabled,Enabled"',
        allow_blank=False,
    )
    ws.add_data_validation(disabled_enabled)

    ws['A3'].value = 'Translation'
    ws['B3'].value = translation['id']
    ws['A4'].value = 'Translation Owner'
    ws['B4'].value = translation['owner']['id']
    ws['A5'].value = 'Locale'
    ws['B5'].value = translation['locale']['id']
    ws['A6'].value = 'Localization Context'
    ws['B6'].value = translation['context']['id']
    ws['A7'].value = 'Instance ID'
    ws['B7'].value = translation['context']['instance_id']
    ws['A8'].value = 'Instance Name'
    ws['B8'].value = translation['context']['name']
    ws['A9'].value = 'Description'
    ws['A9'].alignment = Alignment(horizontal='left', vertical='top')
    ws['B9'].value = translation['description']
    ws['B9'].alignment = Alignment(wrap_text=True)
    ws['A10'].value = 'Autotranslation'
    ws['B10'].value = 'Enabled' if translation['auto']['enabled'] else 'Disabled'
    disabled_enabled.add(ws['B10'])


def _set_ws_main_header(ws, title):
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 180
    ws.merge_cells('A1:B1')
    cell = ws['A1']
    cell.fill = PatternFill('solid', start_color=Color('1565C0'))
    cell.font = Font(sz=24, color=WHITE)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.value = title
