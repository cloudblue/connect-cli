import os
import sys

from datetime import datetime
from importlib import import_module

import click

from cnct import R
from interrogatio import dialogus

from openpyxl import load_workbook


def get_report_entrypoint(func_fqn):
    module_name, func_name = func_fqn.rsplit('.', 1)
    try:
        module = import_module(module_name)
        return getattr(module, func_name)
    except ImportError:
        pass
    except AttributeError:
        pass


def get_report_inputs(client, parameters):
    # if acc_id.startswith('VA'):
    #     default_query = R().visibility.owner.eq(True) & R().version.null(True)
    # else:
    #     default_query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)
    questions = []
    for param in parameters:
        if param['type'] == 'daterange':
            questions.extend([
                {
                    'name': f'{param["id"]}_after',
                    'type': 'input',
                    'message': f'{param["name"]} after',
                },
                {
                    'name': f'{param["id"]}_before',
                    'type': 'input',
                    'message': f'{param["name"]} before',
                },
            ])
        if param['type'] == 'product_list':
            products = client.products.filter(status='published')
            products = products.filter(R().visibility.owner.eq(True) & R().version.null(True))
            questions.append(
                {
                    'name': param['id'],
                    'type': 'selectmany',
                    'message': param['name'],
                    'values': [
                        (p['name'], p['id'])
                        for p in products
                    ],
                }
            )
    click.echo(questions)
    answers = dialogus(
        questions,
        'Enter your report parameters',
        confirm='Run',
    )
    param_values = {}
    for param in parameters:
        if param['type'] == 'daterange':
            after_str = answers[f"{param['id']}_after"]
            before_str = answers[f"{param['id']}_before"]
            after = datetime.strptime(after_str, '%Y-%m-%d').isoformat()
            before = datetime.strptime(before_str, '%Y-%m-%d').isoformat()
            param_values[param['id']] = {
                'after': after,
                'before': before,
            }
            continue
        param_values[param['id']] = answers[param['id']]
    return param_values


def execute_report(client, reports_dir, report, output_file):
    sys.path.append(reports_dir)
    entrypoint = get_report_entrypoint(report['entrypoint'])
    click.echo(f'Entrypoint {entrypoint}')
    inputs = get_report_inputs(client, report['parameters'])

    template_workbook = load_workbook(
        os.path.join(
            reports_dir,
            report['template'],
        ),
    )

    ws = template_workbook['Report']

    row_idx = report['start_row']
    start_col_idx = report['start_col']

    for row in entrypoint(client, inputs, lambda p, m: None):
        for col_idx, cell_value in enumerate(row, start=start_col_idx):
            ws.cell(row_idx, col_idx, value=cell_value)

    template_workbook.save(output_file)
