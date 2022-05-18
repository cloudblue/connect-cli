from collections import OrderedDict

import pytest

from connect.cli.plugins.project import utils


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
    sorted_tags = utils.sort_and_filter_tags(tags, '21')
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
    assert (utils._ConnectVersionTag(str).plain_tag is None) == result


@pytest.mark.parametrize(
    'value',
    (
        '0.2.0',
        'plain-tag-0.0.2a2',
    ),
)
def test_connect_version_tag_eq_comparison(value):
    first = utils._ConnectVersionTag(value)
    assert first == value
    assert first == utils._ConnectVersionTag(value)


def test_connect_version_tag_invalid_comparison():
    assert not utils._ConnectVersionTag(str) == 10
