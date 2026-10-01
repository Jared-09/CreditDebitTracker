from unittest.mock import Mock

from app.plaid_sync import sync_transactions


def test_sync_transactions_first_sync():

    client = Mock()

    response = Mock()
    response.added = [
        {
            "transaction_id": "txn_001",
            "amount": 25.00,
        }
    ]
    response.modified = []
    response.removed = []
    response.next_cursor = "cursor_001"

    client.transactions_sync.return_value = response

    result = sync_transactions(
        client=client,
        access_token="test-access-token",
        cursor=None,
    )

    assert result["added"] == [
        {
            "transaction_id": "txn_001",
            "amount": 25.00,
        }
    ]

    assert result["next_cursor"] == "cursor_001"

    client.transactions_sync.assert_called_once()