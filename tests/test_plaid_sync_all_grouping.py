from unittest.mock import patch

from app.plaid_sync_all import (
    sync_all_plaid_accounts,
)


def test_each_plaid_item_is_synced_once():

    links = [
        {
            "item_id": "item-1",
            "account_id": 10,
        },
        {
            "item_id": "item-1",
            "account_id": 11,
        },
        {
            "item_id": "item-2",
            "account_id": 20,
        },
    ]

    with patch(
        "app.plaid_sync_all.get_all_plaid_account_links",
        return_value=links,
    ), patch(
        "app.plaid_sync_all.sync_account_from_plaid",
        return_value={
            "account_id": 10,
            "added": 2,
            "modified": 0,
            "removed": 0,
        },
    ) as mock_sync:

        results = sync_all_plaid_accounts(
            client="test-client"
        )

    assert mock_sync.call_count == 2

    synced_item_ids = {
        call.kwargs["item_id"]
        for call in mock_sync.call_args_list
    }

    assert synced_item_ids == {
        "item-1",
        "item-2",
    }

    results_by_item = {
        result["linked_account_ids"][0]: result
        for result in results
    }

    linked_account_sets = [
        sorted(result["linked_account_ids"])
        for result in results
    ]

    assert sorted(linked_account_sets) == [
        [10, 11],
        [20],
    ]