import os.path
from collections import OrderedDict

import pytest
from click import ClickException
from requests import RequestException

from connect.cli.core import utils
from connect.cli.core.constants import PYPI_JSON_API_URL
from connect.cli.core.utils import (
    iter_entry_points,
    sort_and_filter_tags,
)


def test_check_for_updates_ok(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='1.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' in captured.out
    assert 'A newer version is available: 2.0.0' in captured.out


def test_check_for_updates_is_latest(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='2.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, json={'info': {'version': '2.0.0'}})

    utils.check_for_updates()

    captured = capsys.readouterr()

    assert 'You are running CloudBlue Connect CLI version 1.0.0. ' not in captured.out
    assert 'A newer version is available: 2.0.0' not in captured.out


def test_check_for_updates_exception(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='1.0.0')
    mocker.patch('connect.cli.core.utils.requests.get', side_effect=RequestException())

    utils.check_for_updates()

    captured = capsys.readouterr()
    assert captured.out == ''


def test_check_for_updates_invalid_response(mocker, capsys, mocked_responses):
    mocker.patch('connect.cli.core.utils.get_version', return_value='1.0.0')
    mocked_responses.add('GET', PYPI_JSON_API_URL, status=400)

    utils.check_for_updates()

    captured = capsys.readouterr()
    assert captured.out == ''


def test_validate_output_options(fs):
    fs.makedirs('custom/path')

    output_file = utils.validate_output_options(
        output_path=os.path.join(fs.root_path, 'custom/path'),
        output_file='custom_filename.xlsx',
        default_dir_name='XX-000-000',
        default_file_name='data.xlsx',
    )

    assert output_file.endswith('custom/path/XX-000-000/custom_filename.xlsx')


def test_validate_output_options_output_path_does_not_exist(fs):
    with pytest.raises(ClickException) as e:
        utils.validate_output_options(
            output_path=os.path.join(fs.root_path, 'custom/inexistent/path'),
            output_file=None,
            default_dir_name='XX-000-000',
        )

    assert 'Output Path does not exist' in str(e)


def test_validate_output_options_output_path_is_file(fs):
    fs.makedirs('custom/path')
    fs.create('custom/path/XX-000-000')

    with pytest.raises(ClickException) as e:
        utils.validate_output_options(
            output_path=os.path.join(fs.root_path, 'custom/path'),
            output_file=None,
            default_dir_name='XX-000-000',
        )

    assert (
        "Exists a file with name 'XX-000-000' but a directory is "
        "expected, please rename it" in str(e)
    )


def test_validate_output_options_no_options(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file=None,
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('workdir/XX-000-000/data.xlsx')


def test_validate_output_options_no_options_no_default_file_name(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file=None,
        default_dir_name='XX-000-000',
    )

    assert output_file.endswith('workdir/XX-000-000/XX-000-000.xlsx')


def test_validate_output_options_no_output_path(fs, mocker):
    fs.makedir('workdir')
    mocker.patch('os.getcwd', return_value=os.path.join(fs.root_path, 'workdir'))

    output_file = utils.validate_output_options(
        output_path=None,
        output_file='custom_filename.xlsx',
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('workdir/XX-000-000/custom_filename.xlsx')


def test_validate_output_options_no_output_file(fs):
    fs.makedirs('custom/path')

    output_file = utils.validate_output_options(
        output_path=os.path.join(fs.root_path, 'custom/path'),
        output_file=None,
        default_dir_name='XX-000-000',
        default_file_name='data',
    )

    assert output_file.endswith('custom/path/XX-000-000/data.xlsx')


def test_field_to_check_mark():
    assert '✓' == utils.field_to_check_mark(True)
    assert '' == utils.field_to_check_mark(False)


def test_field_to_check_mark_with_false_value():
    assert '-' == utils.field_to_check_mark(False, false_value='-')


@pytest.mark.parametrize(
    ('tags', 'expected'),
    (
        (
            {'v21.1': 'cmt1', 'v21.10': 'cmt2', 'v21.11': 'cmt3', 'v21.9': 'cmt4'},
            OrderedDict({'v21.1': 'cmt1', 'v21.9': 'cmt4', 'v21.10': 'cmt2', 'v21.11': 'cmt3'}),
        ),
        (
            {'21.1': 'cmt1', '21.10': 'cmt2', '21.11': 'cmt3', '21.9': 'cmt4'},
            OrderedDict({'21.1': 'cmt1', '21.9': 'cmt4', '21.10': 'cmt2', '21.11': 'cmt3'}),
        ),
        (
            {'21.1': 'cmt1', '21.10': 'cmt2', '21.9': 'cmt4', '23.0.1a2': 'cmt3'},
            OrderedDict({'21.1': 'cmt1', '21.9': 'cmt4', '21.10': 'cmt2'}),
        ),
        (
            {'21.1': 'cmt1', '21.10': 'cmt2', '21.9': 'cmt4', '21.0.1a2': 'cmt3'},
            OrderedDict({'21.0.1a2': 'cmt3', '21.1': 'cmt1', '21.9': 'cmt4', '21.10': 'cmt2'}),
        ),
        (
            {'01.1': 'cmt1', '21.10': 'cmt2', '21.11': 'cmt3', '21.9': 'cmt4'},
            OrderedDict({'21.9': 'cmt4', '21.10': 'cmt2', '21.11': 'cmt3'}),
        ),
        (
            {'v21.10not-a-tag': 'cmt5', '01.1': 'cmt1', '21.11': 'cmt3', '21.10': 'cmt2', 'v21.11': 'cmt4'},
            OrderedDict(
                {
                    '21.10': 'cmt2',
                    '21.11': 'cmt3',
                    'v21.11': 'cmt4',
                },
            ),
        ),
        (
            {
                'not-a-version-tag': 'cmt1',
                '21.1': 'cmt5',
                '21.10a1': 'cmt7alpha',
                '21.10': 'cmt7',
                'not-a-version-tag3': 'cmt3',
                '22a2': 'cmt4',
                'not-a-version-tag2': 'cmt2',
                '21.9': 'cmt6',
                '23.0.1a2': 'cmt8',
            },
            OrderedDict(
                {
                    '21.1': 'cmt5',
                    '21.9': 'cmt6',
                    '21.10a1': 'cmt7alpha',
                    '21.10': 'cmt7',
                },
            ),
        ),
        ({}, OrderedDict()),
    ),
)
def test_sort_and_filter_tags(tags, expected):
    sorted_tags = sort_and_filter_tags(tags, '21')
    assert sorted_tags == expected


def test_iter_entry_points(mocker):
    ep1 = mocker.MagicMock()
    ep1.name = 'ep1'
    ep2 = mocker.MagicMock()
    ep2.name = 'ep2'
    mocker.patch(
        'connect.cli.core.utils.entry_points',
        return_value={'ep.group': [ep1, ep2]},
    )

    assert list(iter_entry_points('ep.group', name='ep1')) == [ep1]
    assert list(iter_entry_points('ep.group')) == [ep1, ep2]
    assert list(iter_entry_points('ep.other_group')) == []
