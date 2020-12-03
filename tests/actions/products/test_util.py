from cnctcli.actions.products.utils import (
    get_col_limit_by_ws_type,
    get_ws_type_by_worksheet_name,
)

# This tests exists just to have them on code coverage, real test depends on sync action


def test_get_col_limit_unknown_type():
    assert 'Z' == get_col_limit_by_ws_type('UNKNOWN')


def test_get_ws_type_by_worksheet():
    assert 'items' == get_ws_type_by_worksheet_name('Items')
    assert 'params' == get_ws_type_by_worksheet_name('Ordering Parameters')
    assert 'params' == get_ws_type_by_worksheet_name('Fulfillment Parameters')
    assert 'params' == get_ws_type_by_worksheet_name('Configuration Parameters')
    assert 'media' == get_ws_type_by_worksheet_name('Media')
    assert 'capabilities' == get_ws_type_by_worksheet_name('Capabilities')
    assert 'static_links' == get_ws_type_by_worksheet_name('Embedding Static Resources')
    assert 'templates' == get_ws_type_by_worksheet_name('Templates')
    assert 'configurations' == get_ws_type_by_worksheet_name('Configuration')
    assert 'actions' == get_ws_type_by_worksheet_name('Actions')
    assert get_ws_type_by_worksheet_name('CUSTOM') is None
