import pytest
from click import ClickException

from cnctcli.api.products import (
    create_item, get_item, get_item_by_mpn,
    get_items, get_product, update_item,
)

from tests.api.helpers import assert_request_headers


def test_get_product(requests_mock):
    product_data = {
        'id': 'PRD-000',
        'name': 'Test product',
    }
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000',
        json=product_data,
    )

    p = get_product(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
    )

    assert p == product_data
    assert mocked.call_count == 1
    assert_request_headers(mocked.request_history[0].headers)


def test_get_product_not_found(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000',
        status_code=404,
    )

    with pytest.raises(ClickException) as e:
        get_product(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
        )

    assert str(e.value) == '404 - Not Found: Product PRD-000 not found.'


def test_get_product_other_errors(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        get_product(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'


def test_get_items(requests_mock):
    items_data = [
        {
            'id': 'PRD-000-0000',
            'name': 'Item 0',
        },
        {
            'id': 'PRD-000-0001',
            'name': 'Item 1',
        },
    ]
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items',
        json=items_data,
        headers={'Content-Range': 'items 0-99/100'},
    )

    count, items = get_items(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
    )

    assert count == 100
    assert items == items_data
    assert mocked.call_count == 1
    params = mocked.request_history[0].qs
    assert 'limit' in params
    assert params['limit'][0] == '100'
    assert 'offset' in params
    assert params['offset'][0] == '0'
    assert_request_headers(mocked.request_history[0].headers)


def test_get_items_product_not_found(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items',
        status_code=404,
    )

    with pytest.raises(ClickException) as e:
        get_items(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
        )

    assert str(e.value) == '404 - Not Found: Product PRD-000 not found.'


def test_get_items_other_errors(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        get_items(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'


def test_get_item(requests_mock):
    item_data = {
        'id': 'PRD-000-0000',
        'mpn': 'mpn_001',
    }
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items/PRD-000-0000',
        json=item_data,
    )

    i = get_item(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        'PRD-000-0000',
    )

    assert i == item_data
    assert mocked.call_count == 1
    assert_request_headers(mocked.request_history[0].headers)


def test_get_item_not_found(requests_mock):
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items/PRD-000-0000',
        status_code=404,
    )

    i = get_item(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        'PRD-000-0000',
    )
    assert mocked.call_count == 1
    assert i is None


def test_get_item_other_errors(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items/PRD-000-0000',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        get_item(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
            'PRD-000-0000',
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'


def test_get_item_by_mpn(requests_mock):
    item_data = [
        {
            'id': 'PRD-000-0000',
            'mpn': 'mpn_001',
        },
    ]
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items?eq(mpn,mpn_001)',
        json=item_data,
    )

    i = get_item_by_mpn(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        'mpn_001',
    )

    assert i == item_data[0]
    assert mocked.call_count == 1
    assert_request_headers(mocked.request_history[0].headers)


def test_get_item_by_mpn_not_found(requests_mock):
    mocked = requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items?eq(mpn,mpn_001)',
        status_code=404,
    )

    i = get_item_by_mpn(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        'mpn_001',
    )
    assert mocked.call_count == 1
    assert i is None


def test_get_item_by_mpn_other_errors(requests_mock):
    requests_mock.get(
        'https://localhost/public/v1/products/PRD-000/items?eq(mpn,mpn_001)',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        get_item_by_mpn(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
            'mpn_001',
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'


def test_create_item(requests_mock):
    mocked = requests_mock.post(
        'https://localhost/public/v1/products/PRD-000/items',
        status_code=201,
        json={'id': 'PRD-000-0000'},
    )

    i = create_item(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        {'mpn': 'mpn_001'},
    )

    assert i == {'id': 'PRD-000-0000'}
    assert mocked.call_count == 1
    assert mocked.request_history[0].json() == {'mpn': 'mpn_001'}
    assert_request_headers(mocked.request_history[0].headers)


def test_create_item_errors(requests_mock):
    requests_mock.post(
        'https://localhost/public/v1/products/PRD-000/items',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        create_item(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
            {'mpn': 'mpn_001'},
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'


def test_update_item(requests_mock):
    mocked = requests_mock.put(
        'https://localhost/public/v1/products/PRD-000/items/PRD-000-0000',
        status_code=200,
        json={'id': 'PRD-000-0000'},
    )

    update_item(
        'https://localhost/public/v1',
        'ApiKey XXXX:YYYY',
        'PRD-000',
        'PRD-000-0000',
        {'mpn': 'mpn_001'},
    )

    assert mocked.call_count == 1
    assert mocked.request_history[0].json() == {'mpn': 'mpn_001'}
    assert_request_headers(mocked.request_history[0].headers)


def test_update_item_errors(requests_mock):
    requests_mock.put(
        'https://localhost/public/v1/products/PRD-000/items/PRD-000-0000',
        status_code=500,
    )

    with pytest.raises(ClickException) as e:
        update_item(
            'https://localhost/public/v1',
            'ApiKey XXXX:YYYY',
            'PRD-000',
            'PRD-000-0000',
            {'mpn': 'mpn_001'},
        )

    assert str(e.value) == '500 - Internal Server Error: unexpected error.'
