import os
import sys
import time

from datetime import datetime
from importlib import import_module

import click

from cnct import R
from interrogatio import dialogus
from tqdm import tqdm

from openpyxl import load_workbook

from cnctcli.actions.products.constants import DEFAULT_BAR_FORMAT


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

    class Progress:
        def __init__(self):
            self.progress = None

        def close(self):
            if self.progress:
                self.progress.close()

        def progress_update(self, value, max_value):
            if not self.progress:
                self.progress = tqdm(
                    desc=f'Processing report {report["name"]}...',
                    total=max_value,
                    leave=True,
                    bar_format=DEFAULT_BAR_FORMAT,
                )
            self.progress.update(value)

    progress = Progress()

    for row in entrypoint(client, inputs, progress.progress_update):
        for col_idx, cell_value in enumerate(row, start=start_col_idx):
            ws.cell(row_idx, col_idx, value=cell_value)

    template_workbook.save(output_file)
    progress.close()
