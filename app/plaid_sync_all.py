from app.plaid_items import (
    get_all_plaid_account_links,
)

from app.plaid_account_sync import (
    sync_account_from_plaid,
)


def sync_all_plaid_accounts(
    client,
):
    """
    Sync every connected Plaid Item once.

    A single Plaid Item can contain multiple accounts,
    so we group account links by Item before syncing.
    """

    links = get_all_plaid_account_links()

    if not links:
        return []

    items = {}

    for link in links:
        item_id = link["item_id"]

        if item_id not in items:
            items[item_id] = {
                "item_id": item_id,
                "account_ids": [],
            }

        items[item_id]["account_ids"].append(
            link["account_id"]
        )

    results = []

    for item in items.values():
        sync_result = sync_account_from_plaid(
            account_id=item["account_ids"][0],
            item_id=item["item_id"],
            client=client,
        )

        result = dict(sync_result)

        result["linked_account_ids"] = list(
            item["account_ids"]
        )

        results.append(result)

    return results