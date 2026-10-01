from unittest.mock import patch

from app.plaid_account_sync import (
    sync_account_from_plaid,
)


def test_sync_account_updates_plaid_balances():

    plaid_item = {
        "access_token": "test-access-token",
        "sync_cursor": None,
    }

    transaction_response = {
        "added": [],
        "modified": [],
        "removed": [],
        "next_cursor": "next-cursor",
    }

    transaction_result = {
        "added": 0,
        "modified": 0,
        "removed": 0,
    }

    balances = [
        {
            "plaid_account_id": "plaid-123",
            "current_balance": 1500.25,
        }
    ]

    with patch(
        "app.plaid_account_sync.get_plaid_item",
        return_value=plaid_item,
    ), patch(
        "app.plaid_account_sync.get_plaid_account_balances",
        return_value=balances,
    ), patch(
        "app.plaid_account_sync.update_account_balance_by_plaid_id",
    ) as mock_update, patch(
        "app.plaid_account_sync.sync_transactions",
        return_value=transaction_response,
    ), patch(
        "app.plaid_account_sync.sync_plaid_transactions",
        return_value=transaction_result,
    ), patch(
        "app.plaid_account_sync.update_plaid_cursor",
    ):

        result = sync_account_from_plaid(
            account_id=1,
            item_id="item-123",
            client="client",
        )

    mock_update.assert_called_once_with(
        plaid_account_id="plaid-123",
        current_balance=1500.25,
    )

    assert result["updated_balances"] == [
        {
            "plaid_account_id": "plaid-123",
            "current_balance": 1500.25,
        }
    ]