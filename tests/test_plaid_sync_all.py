from unittest.mock import Mock

from app.plaid_items import (
    save_plaid_item,
    link_plaid_item_to_account,
)

from app.accounts import add_account

from app.plaid_sync_all import (
    sync_all_plaid_accounts,
)


def test_sync_all_plaid_accounts(
    test_database,
):

    account_id = add_account(
        name="Test Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
        account_role="credit_card",
    )

    save_plaid_item(
        item_id="item_all_test",
        access_token="access_test",
    )

    link_plaid_item_to_account(
        item_id="item_all_test",
        account_id=account_id,
    )

    client = Mock()

    response = Mock()
    response.added = []
    response.modified = []
    response.removed = []
    response.next_cursor = "cursor_all"

    client.transactions_sync.return_value = response

    result = sync_all_plaid_accounts(
        client
    )

    assert len(result) == 1
    assert result[0]["account_id"] == account_id