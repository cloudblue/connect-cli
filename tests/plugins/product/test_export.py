import pytest

from connect.cli.plugins.product.export import _primary_translation_str


def test_primary_translation_str_ok():
    translation = {
        'locale': {
            'id': 'jp',
            'name': 'Japanese',
        }
    }

    assert 'jp (Japanese)' == _primary_translation_str(translation)


def test_primary_translation_str_none():
    assert '' == _primary_translation_str(None)
