import json
import sys
import traceback
from datetime import timezone
from importlib import import_module
from threading import Lock

from click import ClickException
from tqdm import tqdm

from connect.cli.core.constants import DEFAULT_BAR_FORMAT
from connect.client import ClientError


def convert_to_utc_input(date):
    return date.astimezone(timezone.utc).isoformat()


def get_report_by_id(repo, local_id):
    try:
        return next(filter(lambda report: report.local_id == local_id, repo.reports))
    except StopIteration:
        raise ClickException(f'The report `{local_id}` does not exist.')


def get_renderer_by_id(report, renderer_id):
    try:
        return next(filter(lambda r: r.id == renderer_id, report.renderers))
    except StopIteration:
        raise ClickException(
            f'The output format `{renderer_id}` is not available for report {report.local_id}.')


def get_report_entrypoint(report):
    sys.path.append(report.root_path)
    module_name, func_name = report.entrypoint.rsplit('.', 1)
    try:
        module = import_module(module_name)
        return getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        raise ClickException(f'Cannot load report code for report {report.local_id}: {str(e)}')


def handle_report_exception():
    _, exc_value, tb = sys.exc_info()
    msg = ''
    if isinstance(exc_value, ClientError):
        msg = f'Error returned by Connect when executing the report: {str(exc_value)}'
    elif isinstance(exc_value, RuntimeError):
        msg = f'Report error: {str(exc_value)}'
    else:
        msg = f'Unexpected error while executing the report: {str(exc_value)}'

    trace = []
    while tb is not None:
        trace.append(
            {
                'filename': tb.tb_frame.f_code.co_filename,
                'name': tb.tb_frame.f_code.co_name,
                'lineno': tb.tb_lineno,
                'info': '\n'.join(traceback.format_tb(tb)),
            },
        )
        tb = tb.tb_next
    trace_string = json.dumps(trace, sort_keys=True, indent=4)
    raise ClickException(f'\n{msg}\nTrace: {trace_string}')


class Progress(tqdm):
    def __init__(self, report_name):
        super().__init__()
        self.lock = Lock()
        self.desc = f'Processing report {report_name}...'
        self.leave = True
        self.bar_format = DEFAULT_BAR_FORMAT
        self.current_value = 0
        self.monitor_interval = 1
        self.miniters = 1

    def __call__(self, value, max_value):
        self.lock.acquire()
        self.total = max_value
        self.update(value - self.current_value)
        self.current_value = value
        self.lock.release()

    def close(self):
        if self.total is None:
            self.total = 100
        if self.current_value < self.total:
            self(self.total, self.total)
        super().close()
