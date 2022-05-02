import re

from connect.cli.plugins.locale.utils import (
    icon_for_autotranslate,
    row_format_resource,
    stats_of_translations,
    table_formater_resource,
)


def test_icon_for_autotranslate(mocked_locales_response):
    assert '✓' == icon_for_autotranslate([d for d in mocked_locales_response if d['auto_translation']][0])
    assert '✖' == icon_for_autotranslate([d for d in mocked_locales_response if not d['auto_translation']][0])


def test_stats_of_translations(mocked_locales_response):
    assert 1 == stats_of_translations([d for d in mocked_locales_response if d['stats']['translations'] > 0][0])
    assert '-' == stats_of_translations([d for d in mocked_locales_response if d['stats']['translations'] == 0][0])


def test_row_format_resource():
    fields = (
        'ZH-HANS',
        'Simplified Chinese',
        '✓',
        '-',
    )
    separators = len(fields) + 1
    assert '| ZH-HANS | Simplified Chinese | ✓ | - |\n' == row_format_resource(*fields)
    assert separators == len(re.findall(r'\|', row_format_resource(*fields)))


header = '|ID|\n|:----:|\n'
resources = ['| ZH-HANS |\n', '| ZH-HANS |\n']


def test_formater_not_echo_with_page_size_greater_than_paging(capsys):

    table_formater_resource(
        resource_str_list=[header, *resources],
        count_of_resources=97,
        paging=1,
        page_size=10,
    )
    captured = capsys.readouterr()
    assert '' == captured.out


def test_table_formater_page_size_equeal_paging(capsys):

    table_formater_resource(
        resource_str_list=[header, resources[0]],
        count_of_resources=97,
        paging=1,
        page_size=1,
    )

    captured = capsys.readouterr()
    assert '┌───────┐\n│   ID  │\n├───────┤\n│ZH-HANS│\n└───────┘\n' == captured.out
