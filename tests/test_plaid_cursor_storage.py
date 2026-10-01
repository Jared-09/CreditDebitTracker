from app.plaid_items import (
    save_plaid_item,
    get_plaid_item,
    update_plaid_cursor,
)


def test_plaid_cursor_can_be_updated(
    test_database,
):

    save_plaid_item(
        item_id="item_cursor_test",
        access_token="access_token",
        sync_cursor="cursor_old",
    )

    update_plaid_cursor(
        item_id="item_cursor_test",
        sync_cursor="cursor_new",
    )

    item = get_plaid_item(
        "item_cursor_test"
    )

    assert item["sync_cursor"] == "cursor_new"