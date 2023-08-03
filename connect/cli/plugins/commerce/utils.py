import os
import json
from datetime import datetime
import string
from urllib.parse import urlparse

from click import ClickException
from connect.cli.core.terminal import console
from connect.client import ClientError
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.styles.colors import WHITE, Color

from connect.cli.core.utils import validate_output_options


def display_streams_table(
    query_billing_streams,
    query_pricing_streams,
    active_account_id,
):
    rows = []
    for origin, query in (
        ('Billing', query_billing_streams),
        ('Pricing', query_pricing_streams),
    ):
        for resource in query:
            rows.append(
                (
                    resource['id'],
                    origin,
                    resource['name'],
                    'Computed' if ('sources' in resource and resource['sources']) else 'Simple',
                    'Inbound' if resource['owner']['id'] != active_account_id else 'Outbound',
                    resource['status'].capitalize(),
                    resource['visibility'].capitalize(),
                ),
            )
    if rows:
        console.table(
            columns=[
                'ID',
                'Business scope',
                'Name',
                'Type',
                'Category',
                'Status',
                'Visibility',
            ],
            rows=rows,
        )
    else:
        console.secho(
            f'Results not found for the current account {active_account_id}.',
            fg='yellow',
        )


def guess_if_billing_or_pricing_stream(client, stream_id):
    if client.ns('billing').streams.filter(id=stream_id).count() > 0:
        return 'billing'
    elif client.ns('pricing').streams.filter(id=stream_id).count() > 0:
        return 'pricing'
    return None


def fill_general_information(ws, data, progress):
    ws.title = 'General Information'
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 180
    ws.merge_cells('A1:B1')
    cell = ws['A1']
    cell.fill = PatternFill('solid', start_color=Color('1565C0'))
    cell.font = Font(sz=24, color=WHITE)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.value = 'Stream information'
    count = len(data)
    task = progress.add_task('Filling general information', total=count)
    for line, key in enumerate(data, 2):
        ws[f'A{line}'] = key
        ws[f'B{line}'] = data[key]
        progress.update(task, advance=1)


def _fill_headers(ws, columns):
    color = Color('d3d3d3')
    fill = PatternFill('solid', color)
    for n, value in enumerate(columns):
        letter = string.ascii_uppercase[n]
        cell = ws[f'{letter}1']
        cell.fill = fill
        cell.value = value


def fill_columns(ws, columns, progress):
    columns = list(columns)
    ws.column_dimensions['A'].width = 22
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 40
    _fill_headers(
        ws,
        (
            'ID',
            'Name',
            'Description',
            'Type',
            'Position',
            'Required',
            'Output',
        ),
    )
    alignment = Alignment(
        horizontal='left',
        vertical='top',
    )
    if len(columns) > 0:
        task = progress.add_task('Filling columns', total=len(columns))
        for n, col in enumerate(columns, 2):
            ws.cell(n, 1, value=col['id']).alignment = alignment
            ws.cell(n, 2, value=col['name']).alignment = alignment
            ws.cell(n, 3, value=col.get('description', '')).alignment = alignment
            ws.cell(n, 4, value=col.get('type', '')).alignment = alignment
            ws.cell(n, 5, value=col['position']).alignment = alignment
            ws.cell(n, 6, value=col['required']).alignment = alignment
            ws.cell(n, 7, value=col['output']).alignment = alignment
            progress.update(task, advance=1)


def fill_transformations(ws, transformations, progress):
    try:
        transformations = list(transformations)
    except ClientError:
        return
    ws.column_dimensions['A'].width = 30
    for column in ('B', 'C', 'D', 'E', 'F', 'G'):
        ws.column_dimensions[column].width = 22
    ws.column_dimensions['H'].width = 40
    _fill_headers(
        ws,
        (
            'ID',
            'Function ID',
            'Function Name',
            'Description',
            'Overview',
            'Input columns',
            'Output Columns',
            'Position',
            'Settings',
        ),
    )
    alignment = Alignment(
        horizontal='left',
        vertical='top',
    )
    if len(transformations) > 0:
        task = progress.add_task('Filling transformations', total=len(transformations))
        for n, transformation in enumerate(transformations, 2):
            ws.cell(n, 1, value=transformation['id']).alignment = alignment
            ws.cell(n, 2, value=transformation['function']['id']).alignment = alignment
            ws.cell(n, 3, value=transformation['function']['name']).alignment = alignment
            ws.cell(n, 4, value=transformation.get('description', '')).alignment = alignment
            ws.cell(n, 5, value=transformation['overview']).alignment = alignment
            col_alignment = Alignment(
                horizontal='left',
                vertical='top',
                wrap_text=True,
            )
            ws.cell(
                n,
                6,
                value='\n'.join([c['id'] for c in transformation['columns']['input']]),
            ).alignment = col_alignment
            ws.cell(
                n,
                7,
                value='\n'.join([c['id'] for c in transformation['columns']['output']]),
            ).alignment = col_alignment
            ws.cell(n, 8, value=transformation['position']).alignment = alignment
            ws.cell(
                n,
                9,
                value=json.dumps(transformation['settings'], indent=4, sort_keys=True),
            ).alignment = col_alignment
            ws.row_dimensions[n].height = 120
            progress.update(task, advance=1)


def _download_file(client, folder_type, folder_name, file_id, file_destination):
    try:
        response = (
            client.ns(
                'media',
            )
            .ns(
                'folders',
            )
            .collection(
                folder_type,
            )[folder_name]
            .collection(
                'files',
            )[file_id]
            .get()
        )
    except ClientError:
        raise ClickException(f'Error obtaining file {file_id} -> {file_destination}')
    with open(file_destination, 'wb') as f:
        f.write(response)


def fill_and_download_attachments(ws, attachments, client, base_path, progress):
    attachments = list(attachments)
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 30
    _fill_headers(
        ws,
        ('ID', 'Name'),
    )
    if len(attachments) > 0:
        task = progress.add_task('Filling and downloading attachments', total=len(attachments))
        for n, attachment in enumerate(attachments, 2):
            ws.cell(n, 1, value=attachment['id'])
            ws.cell(n, 2, value=attachment['name'])
            _download_file(
                client=client,
                folder_type=attachment['folder']['type'],
                folder_name=attachment['folder']['name'],
                file_id=attachment['id'],
                file_destination=os.path.join(base_path, attachment['name']),
            )
            progress.update(task, advance=1)


def export_stream(
    client,
    stream_id,
    active_account_id,
    output_file,
    output_path=None,
):
    output_file = validate_output_options(output_path, output_file, default_dir_name=stream_id)
    attachments_path = os.path.join(os.path.dirname(output_file), 'attachments')
    if not os.path.exists(attachments_path):
        os.mkdir(attachments_path)
    sample_input_path = os.path.join(os.path.dirname(output_file), 'sample', 'input')
    if not os.path.exists(sample_input_path):
        os.makedirs(sample_input_path)

    with console.status_progress() as (status, progress):
        collection = guess_if_billing_or_pricing_stream(client, stream_id)
        if not collection:
            console.secho(
                f'Stream {stream_id} not found for the current account {active_account_id}.',
                fg='red',
            )
            return

        response = (
            client.ns(collection)
            .streams.filter(id=stream_id)
            .select(
                'context',
                'samples',
                'sources',
            )
            .first()
        )

        wb = Workbook()

        stream_type = 'Computed' if 'sources' in response and response['sources'] else 'Simple'
        input = response['samples'].get('input', {})
        input_file_name = urlparse(input.get('name', '/')).path.split('/')[-1]
        status.update('Extracting general information', fg='blue')
        fill_general_information(
            ws=wb.active,
            data={
                'Stream ID': stream_id,
                'Stream Name': response['name'],
                'Stream Description': response['description'],
                'Stream Type': stream_type,
                'Stream Category': 'Inbound'
                if response['owner']['id'] != active_account_id
                else 'Outbound',
                'Computed Stream Source ID': response['sources'][0]['id']
                if stream_type == 'Computed'
                else '',
                'Computed Stream Source Name': response['sources'][0]['name']
                if stream_type == 'Computed'
                else '',
                'Computed Stream Source Type': response['sources'][0]['type']
                if stream_type == 'Computed'
                else '',
                'Product ID': response['context'].get('product', {}).get('id', ''),
                'Product Name': response['context'].get('product', {}).get('name', ''),
                'Partner ID': response['context'].get('account', {}).get('id', ''),
                'Partner Name': response['context'].get('account', {}).get('name', ''),
                'Marketplace ID': response['context'].get('marketplace', {}).get('id', ''),
                'Marketplace Name': response['context'].get('marketplace', {}).get('name', ''),
                'Pricelist ID': response['context'].get('pricelist', {}).get('id', ''),
                'Pricelist Name': response['context'].get('pricelist', {}).get('name', ''),
                'Listing ID': response['context'].get('listing', {}).get('id', ''),
                'Visibility': response['visibility'],
                'Input Data': input_file_name,
                'Export datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%M.%f'),
            },
            progress=progress,
        )

        if input:
            extracted_stream = input['name'].split('/')[-4]
            status.update('Downloading sample file', fg='blue')
            _download_file(
                client=client,
                folder_type='streams_samples',
                folder_name=extracted_stream,
                file_id=input.get('id', None),
                file_destination=os.path.join(sample_input_path, input_file_name),
            )

        status.update('Extracting columns', fg='blue')
        fill_columns(
            wb.create_sheet('Columns'),
            client.ns(collection).streams[stream_id].columns.all(),
            progress=progress,
        )

        status.update('Extracting transformations', fg='blue')
        fill_transformations(
            wb.create_sheet('Transformations'),
            client.ns(collection).streams[stream_id].transformations.all().select('columns'),
            progress=progress,
        )

        status.update('Extracting attachments', fg='blue')
        fill_and_download_attachments(
            wb.create_sheet('Attachments'),
            client.ns('media')
            .ns('folders')
            .collection('streams_attachments')[stream_id]
            .files.all(),
            client,
            base_path=attachments_path,
            progress=progress,
        )

        wb.save(output_file)

    console.secho(
        f'Stream {stream_id} exported properly to {output_file}.',
        fg='green',
    )
