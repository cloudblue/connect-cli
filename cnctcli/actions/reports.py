import os
import sys
import json

from datetime import datetime
from importlib import import_module

import click
from click import ClickException

from interrogatio import dialogus
from tqdm import tqdm

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.styles.colors import Color, WHITE
from cnct import ConnectClient

from cnctcli.actions.products.constants import DEFAULT_BAR_FORMAT
from cnctcli.constants import REPORT_PARAM_TYPES
from cnctcli.actions.reports_params import (
    date_range,
    product_list,
    fulfillment_request_type,
    fulfillment_request_status,
    marketplace_list,
    hubs_list,
    connection_type,
)


def get_report_entrypoint(func_fqn):
    module_name, func_name = func_fqn.rsplit('.', 1)
    try:
        module = import_module(module_name)
        return getattr(module, func_name)
    except ImportError:
        pass
    except AttributeError:
        pass


def get_report_inputs(config, client, parameters):
    parameters_values = {}
    i = 0
    for param in parameters:
        questions = []
        if param['type'] == 'daterange':
            questions.extend(date_range(param))
        if param['type'] == 'product_list':
            questions.append(
                product_list(config.active, client, param)
            )
        if param['type'] == 'fulfillment_type_list':
            questions.append(
                fulfillment_request_type(param)
            )
        if param['type'] == 'fulfillment_status_list':
            questions.append(
                fulfillment_request_status(param)
            )
        if param['type'] == 'marketplace_list':
            questions.append(
                marketplace_list(client, param)
            )
        if param['type'] == 'hubs_list':
            questions.append(
                hubs_list(client, param)
            )
        if param['type'] == 'connection_type':
            questions.append(
                connection_type(param)
            )
        answers = dialogus(
            questions,
            'Enter your report parameters',
            confirm='Run' if i == len(parameters) else 'Next',
        )

        if not answers:
            raise ClickException("Aborted by user input")

        if param['type'] == 'daterange':
            after_str = answers[f"{param['id']}_after"]
            before_str = answers[f"{param['id']}_before"]
            after = datetime.strptime(after_str, '%Y-%m-%d').isoformat()
            before = datetime.strptime(before_str, '%Y-%m-%d').isoformat()
            parameters_values[param['id']] = {
                'after': after,
                'before': before,
            }
            continue
        if questions[0]['type'] == 'selectmany' and \
                len(questions[0]['values']) == len(answers[param['id']]):
            parameters_values[param['id']] = None
        else:
            parameters_values[param['id']] = answers[param['id']]
        i += 1
    return parameters_values


def execute_report(config, reports_dir, report, output_file):
    sys.path.append(reports_dir)
    validate_report_definition(report, reports_dir)



    client = ConnectClient(
        config.active.api_key,
        endpoint=config.active.endpoint,
        use_specs=False,
    )

    entrypoint = get_report_entrypoint(report['entrypoint'])
    inputs = get_report_inputs(config, client, report['parameters'])

    template_workbook = load_workbook(
        os.path.join(
            reports_dir,
            report['template'],
        ),
    )

    ws = template_workbook['Data']

    row_idx = report['start_row']
    start_col_idx = report['start_col']

    class Progress(tqdm):
        def __init__(self):
            super().__init__()
            self.desc = f'Processing report {report["name"]}...'
            self.leave = True
            self.bar_format = DEFAULT_BAR_FORMAT
            self.current_value = 0
            self.monitor_interval = 1
            self.miniters = 1

        def __call__(self, value, max_value):
            self.total = max_value
            self.update(value - self.current_value)
            self.current_value = value

    click.echo(f'Preparing to run report {report["id"]}. Please wait...\n')

    progress = Progress()

    start_time = datetime.now().isoformat()
    for row in entrypoint(client, inputs, progress):
        for col_idx, cell_value in enumerate(row, start=start_col_idx):
            ws.cell(row_idx, col_idx, value=cell_value)
        row_idx += 1
    add_info_sheet(template_workbook.create_sheet('Info'), config, report, inputs, start_time)
    template_workbook.save(output_file)
    progress.close()


def add_info_sheet(ws, config, report, report_values, start_time):
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 180
    ws['A1'].value = "Report Execution Information"
    ws.merge_cells('A1:B1')
    ws['A1'].fill = PatternFill('solid', start_color=Color('1565C0'))
    ws['A1'].font = Font(sz=24, color=WHITE)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    for i in range (2,9):
        ws[f'A{i}'].alignment = Alignment(
            horizontal='left',
            vertical='top',
        )
        ws[f'B{i}'].alignment = Alignment(
            horizontal='left',
            vertical='top',
        )
    ws['A2'].value = "Report Start time"
    ws['B2'].value = start_time
    ws['A3'].value = "Account ID"
    ws['B3'].value = config.active.id
    ws['A4'].value = "Account Name"
    ws['B4'].value = config.active.name
    ws['A5'].value = "Report ID"
    ws['B5'].value = report['id']
    ws['A6'].value = "Report Name"
    ws['B6'].value = report['name']
    ws['A7'].value = "Report Description"
    ws['B7'].value = report['description']
    ws['A8'].value = "Runtime environment"
    ws['B8'].value = "CLI Tool"
    ws['A9'].value = "Report execution paramters"
    ws['B9'].value = json.dumps(report_values, indent=4, sort_keys=True)
    ws['B9'].alignment = Alignment(
        horizontal='left',
        vertical='top',
        wrap_text=True,
    )


def validate_report_json(descriptor, reports_dir):
    if 'name' not in descriptor:
        raise ClickException('Name property is required for reports.json')
    if 'description' not in descriptor:
        raise ClickException('Description property is required for reports.json')
    if 'version' not in descriptor:
        raise ClickException('Version property is required for reports.json')
    if 'reports' not in descriptor:
        raise ClickException('"No reports declared in reports.json')
    for report in descriptor['reports']:
        validate_report_definition(report, reports_dir)


def validate_report_definition(definition, reports_dir):
    if 'id' not in definition:
        raise ClickException("Report without ID found on reports.json")
    required_properties = [
        'name',
        'description',
        'template',
        'start_row',
        'start_col',
        'entrypoint',
    ]
    for required_prop in required_properties:
        if required_prop not in definition:
            raise ClickException(
                f'Property {required_prop} not found for report {definition["id"]}'
            )
    if 'parameters' not in definition:
        raise ClickException(
            f'Missing parameters list for report {definition["id"]}'
        )
    for param in definition['parameters']:
        validate_report_parameters(param, definition['id'])
    if not os.path.isfile(os.path.join(
        reports_dir,
        definition['template']
    )):
        raise ClickException(
            f'Template {definition["template"]} not found on {reports_dir}'
        )


def validate_report_parameters(report_parameters, report_id):
    if 'id' not in report_parameters:
        raise ClickException(
            f'Missing id on parameters for report {report_id}'
        )
    if 'type' not in report_parameters:
        raise ClickException(
            f'Missing type for input parameter {report_parameters["id"]} on report {report_id}'
        )
    if report_parameters['type'] not in REPORT_PARAM_TYPES:
        raise ClickException(
            f'Report {report_id} has a unknown parameter type {report_parameters["type"]} defined '
            f'for parameter {report_parameters["id"]}'
        )
