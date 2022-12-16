from collections import namedtuple

import pytest
from click import ClickException

from connect.cli.plugins.report.utils import (
    get_renderer_by_id,
    get_report_by_id,
    get_report_entrypoint,
)


Repo = namedtuple('Repo', ('reports',))
Report = namedtuple('Report', ('local_id', 'renderers', 'root_path', 'entrypoint'))
Renderer = namedtuple('Renderer', ('id',))


def test_get_renderer_by_id():
    renderers = [Renderer('renderer_id'), Renderer('renderer1_id')]
    report = Report('local_id', renderers, None, None)

    renderer = get_renderer_by_id(report, 'renderer_id')
    assert renderer == renderers[0]


def test_get_renderer_by_id_not_found():
    renderers = [Renderer('renderer_id'), Renderer('renderer1_id')]
    report = Report('local_id', renderers, None, None)

    with pytest.raises(ClickException) as cv:
        get_renderer_by_id(report, 'renderer2_id')

    assert str(cv.value) == 'The output format `renderer2_id` is not available for report local_id.'


def test_get_report_by_id():
    reports = [Report('local_id', None, None, None), Report('local2_id', None, None, None)]
    repo = Repo(reports)

    report = get_report_by_id(repo, 'local_id')
    assert report == reports[0]


def test_get_report_by_id_not_found():
    reports = [Report('local_id', None, None, None), Report('local2_id', None, None, None)]
    repo = Repo(reports)

    with pytest.raises(ClickException) as cv:
        get_report_by_id(repo, 'local3_id')

    assert str(cv.value) == 'The report `local3_id` does not exist.'


def test_get_report_entrypoint(mocker):
    entrypoint = mocker.MagicMock()

    module = mocker.MagicMock()
    module.entrypoint = entrypoint

    report = Report(
        'local_id',
        None,
        'root_path',
        'reports.my_report.entrypoint',
    )
    mocker.patch('connect.cli.plugins.report.utils.import_module', return_value=module)

    ep = get_report_entrypoint(report)
    assert ep == entrypoint


@pytest.mark.parametrize('exc', (ImportError, AttributeError))
def test_get_report_entrypoint_fail(mocker, exc):
    entrypoint = mocker.MagicMock()

    module = mocker.MagicMock()
    module.entrypoint = entrypoint

    report = Report(
        'local_id',
        None,
        'root_path',
        'reports.my_report.entrypoint',
    )
    mocker.patch('connect.cli.plugins.report.utils.import_module', side_effect=exc('test'))

    with pytest.raises(ClickException) as cv:
        get_report_entrypoint(report)

    assert 'Cannot load report code for report local_id:' in str(cv.value)
