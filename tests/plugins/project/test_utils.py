from collections import OrderedDict
import stat

import pytest

from connect.cli.plugins.project.utils import (
    _ConnectVersionTag,
    force_delete,
    purge_dir,
    sort_and_filter_tags,
)


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


@pytest.mark.parametrize(
    ('str', 'result'),
    (
        ('0.0.0', True),
        ('0.0.4', True),
        ('1.0.0', True),
        ('1.2.0', True),
        ('1.2.3', True),
        ('0.0', True),
        ('1.0', True),
        ('10.20', True),
        ('99999999999999999999999.999999999999999999.99999999999999999', True),
        ('v0.0.4', True),
        ('v1.2', True),
        ('v01.23', True),
        ('01.23', True),
        ('01.23a1', True),
        ('01.23b3', True),
        ('01.23rc1', False),
        ('1.1.2-prerelease+meta', False),
        ('1.v2.0', False),
        ('1.', False),
        ('v1', False),
    ),
)
def test_connect_version_tag(str, result):
    assert (_ConnectVersionTag(str).plain_tag is None) == result


@pytest.mark.parametrize(
    'value',
    (
        '0.2.0',
        'plain-tag-0.0.2a2',
    ),
)
def test_connect_version_tag_eq_comparison(value):
    first = _ConnectVersionTag(value)
    assert first == value
    assert first == _ConnectVersionTag(value)


def test_connect_version_tag_invalid_comparison():
    assert not _ConnectVersionTag(str) == 10


def test_force_delete(mocker):
    mocked_os_chmod = mocker.patch('connect.cli.plugins.project.utils.os.chmod')
    mocked_f = mocker.MagicMock()
    force_delete(mocked_f, 'somepath', None)
    mocked_os_chmod.assert_called_with('somepath', stat.S_IWRITE)
    assert mocked_f.call_count == 1


def test_purge_dir(mocker):
    mocked_os_isdir = mocker.patch('connect.cli.plugins.project.utils.os.path.isdir', return_value=True)
    mocked_shutil_rmtree = mocker.patch('connect.cli.plugins.project.utils.shutil.rmtree')
    mocked_force_delete = mocker.patch('connect.cli.plugins.project.utils.force_delete')
    purge_dir('somepath')
    mocked_os_isdir.assert_called_with('somepath')
    mocked_shutil_rmtree.assert_called_with('somepath', onerror=mocked_force_delete)
