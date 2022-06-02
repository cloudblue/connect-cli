import requests
from openpyxl.utils import get_column_letter

from connect.client import RequestLogger


def insert_column_ws(ws, column, width=None):
    """
    Insert a column in a worksheet keeping the width of existing columns.
    """
    column_widths = _get_column_widths(ws, total_columns=max(column, ws.max_column))
    if width is None:
        width = column_widths[column - 1]
    column_widths.insert(column - 1, width)
    ws.insert_cols(idx=column, amount=1)
    _set_column_widths(ws, column_widths)


def _get_column_widths(ws, total_columns):
    return [
        ws.column_dimensions[
            get_column_letter(column)
        ].width for column in range(1, total_columns + 1)
    ]


def _set_column_widths(ws, column_widths):
    for column, column_width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(column)].width = column_width


def logged_request(method, url, verbose=False, **kwargs):
    """
    Make a request with optional logging using the connect OpenAPI client logger
    for consistency with the rest of Connect CLI tool.
    """
    request_logger = RequestLogger(file=None) if verbose else None
    if request_logger:
        request_logger.log_request(method, url, kwargs)
    response = requests.request(method, url, **kwargs)
    if request_logger:
        request_logger.log_response(response)
    return response
