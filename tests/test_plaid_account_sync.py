from unittest.mock import Mock

from app.plaid_account_sync import (
    sync_account_from_plaid,
)
from app.plaid_items import (
    save_plaid_item,
)


def test_sync_account_from_plaid(
    test_database,
):
    client = Mock()

    response = Mock()
    response.added = []
    response.modified = []
    response.removed = []
    response.next_cursor = "cursor_123"

    client.transactions_sync.return_value = response

    save_plaid_item(
        item_id="item_123",
        access_token="access_123",
    )

    result = sync_account_from_plaid(
        account_id=1,
        item_id="item_123",
        client=client,
    )

    assert result["added"] == 0
    assert result["next_cursor"] == "cursor_123"

    client.transactions_sync.assert_called_once()