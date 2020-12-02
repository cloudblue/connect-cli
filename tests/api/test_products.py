import pytest
from click.exceptions import ClickException
from cnct import ConnectClient, ClientError

from cnctcli.api.products import (
    create_unit,
    create_item,
    get_item,
    get_item_by_mpn,
    update_item,
    delete_item,
)


def test_get_item(
        mocked_responses,
        mocked_items_response,
):
    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json=mocked_items_response[0]
    )

    item = get_item(
        client=client,
        product_id='PRD-276-377-545',
        item_id='PRD-276-377-545-0001'
    )

    assert item == mocked_items_response[0]


def test_get_item_exception_404(
        mocked_responses
):
    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        status=404
    )

    item = get_item(
        client=client,
        product_id='PRD-276-377-545',
        item_id='PRD-276-377-545-0001'
    )

    assert item is None


def test_get_item_exception_500(
        mocked_responses
):
    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        status=500
    )

    with pytest.raises(ClickException) as e:
        get_item(
            client=client,
            product_id='PRD-276-377-545',
            item_id='PRD-276-377-545-0001'
        )
    assert str(e.value) == "500 - Internal Server Error: unexpected error."


def test_create_unit(
        mocked_responses
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/settings/units',
        json={
            "id": "unit",
            "name": "unit-k",
        },
        status=200,
    )
    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    result = create_unit(
        client=client,
        data={
            "name": "unit-k",
        }
    )
    assert result['id'] == 'unit'
    assert mocked_responses.assert_all_requests_are_fired


def test_create_unit_500(
        mocked_responses
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/settings/units',
        status=500,
    )
    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    with pytest.raises(ClickException) as e:
        create_unit(
            client=client,
            data={
                "name": "unit-k",
            }
        )
    assert str(e.value) == "500 - Internal Server Error: unexpected error."


def test_get_item_by_mpn(
        mocked_responses,
        mocked_items_response,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[mocked_items_response[0]],
        status=200,
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    item = get_item_by_mpn(
        client=client,
        product_id='PRD-276-377-545',
        mpn='MPN-R-001',
    )

    assert item == mocked_items_response[0]


def test_get_item_by_mpn_500(
        mocked_responses,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,MPN-R-001)&limit=100&offset=0',
        status=500,
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    with pytest.raises(ClickException) as e:
        get_item_by_mpn(
            client=client,
            product_id='PRD-276-377-545',
            mpn='MPN-R-001',
        )
    assert str(e.value) == "500 - Internal Server Error: unexpected error."


def test_get_item_by_mpn_404(
        mocked_responses,
):
    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/items?eq(mpn,'
            'MPN-R-001)&limit=100&offset=0',
        json=[],
        status=404,
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )


    item = get_item_by_mpn(
        client=client,
        product_id='PRD-276-377-545',
        mpn='MPN-R-001',
    )

    assert item is None


def test_create_item(
        mocked_responses,
        mocked_items_response,
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json=mocked_items_response[0]
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    item = create_item(
        client=client,
        product_id='PRD-276-377-545',
        data=mocked_items_response[0]
    )

    assert item == mocked_items_response[0]
    assert mocked_responses.assert_all_requests_are_fired


def test_create_item_409(
        mocked_responses,
        mocked_items_response,
):
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/items',
        json={
            "error_code": "VAL_001",
            "errors": [
                "name: Item with same name already exists for the product.",
                "mpn: Item with same mpn already exists for the product."
            ]
        },
        status=400
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    with pytest.raises(ClickException) as e:
        create_item(
            client=client,
            product_id='PRD-276-377-545',
            data=mocked_items_response[0]
        )

    assert "400 - Bad Request: VAL_001 " in str(e.value)


def test_update_item(
    mocked_responses,
    mocked_items_response,
):
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json=mocked_items_response[0],
        status=200
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    item = update_item(
        client=client,
        product_id='PRD-276-377-545',
        item_id='PRD-276-377-545-0001',
        data=mocked_items_response[0],
    )

    assert item == mocked_items_response[0]


def test_update_item_mpn_exists(
    mocked_responses,
    mocked_items_response,
):
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json={
          "error_code": "VAL_001",
          "errors": [
            "mpn: Item with same mpn already exists for the product."
          ]
        },
        status=400
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    with pytest.raises(ClickException) as e:
        update_item(
            client=client,
            product_id='PRD-276-377-545',
            item_id='PRD-276-377-545-0001',
            data=mocked_items_response[0],
        )

    assert 'Item with same mpn already exists for the product.' in str(e.value)


def test_delete_item(
    mocked_responses
):
    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json={},
        status=204
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    delete_item(
        client=client,
        product_id='PRD-276-377-545',
        item_id='PRD-276-377-545-0001',
    )

    assert mocked_responses.assert_all_requests_are_fired


def test_delete_item_published(
    mocked_responses
):
    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/items/PRD-276-377-545-0001',
        json={
          "error_code": "PRD_038",
          "errors": [
            "Only draft Item can be deleted."
          ]
        },
        status=400
    )

    client = ConnectClient(
        api_key='ApiKey SU:123',
        use_specs=False,
        endpoint='https://localhost/public/v1',
    )

    with pytest.raises(ClickException) as e:
        delete_item(
            client=client,
            product_id='PRD-276-377-545',
            item_id='PRD-276-377-545-0001',
        )

    assert 'Only draft Item can be deleted.' in str(e.value)
