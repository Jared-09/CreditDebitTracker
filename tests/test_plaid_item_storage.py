from app.plaid_items import (
    save_plaid_item,
    get_plaid_item,
)


def test_save_and_get_plaid_item(
    test_database,
):
    save_plaid_item(
        item_id="test-item-id",
        access_token="test-access-token",
    )

    item = get_plaid_item(
        "test-item-id",
    )

    assert item is not None
    assert item["item_id"] == "test-item-id"
    assert item["access_token"] == "test-access-token"
    assert item["sync_cursor"] is None


def test_update_existing_plaid_item_cursor(
    test_database,
):
    save_plaid_item(
        item_id="test-item-id",
        access_token="test-access-token",
    )

    save_plaid_item(
        item_id="test-item-id",
        access_token="test-access-token",
        sync_cursor="cursor-123",
    )

    item = get_plaid_item(
        "test-item-id",
    )

    assert item["sync_cursor"] == "cursor-123"