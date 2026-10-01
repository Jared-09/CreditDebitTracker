from app.accounts import (
    update_account_balance_by_plaid_id,
)

from app.plaid import (
    get_plaid_account_balances,
)

from app.plaid_items import (
    get_plaid_item,
    update_plaid_cursor,
)

from app.plaid_sync import (
    sync_transactions,
)

from app.plaid_pipeline import (
    sync_plaid_transactions,
)


def sync_account_from_plaid(
    account_id,
    item_id,
    client,
):
    """
    Sync one Plaid Item's transactions and balances.
    """

    plaid_item = get_plaid_item(
        item_id
    )

    if plaid_item is None:
        raise ValueError(
            "Plaid Item not found."
        )

    access_token = plaid_item[
        "access_token"
    ]

    balances = get_plaid_account_balances(
        client=client,
        access_token=access_token,
    )

    updated_balances = []

    for balance in balances:

        plaid_account_id = balance[
            "plaid_account_id"
        ]

        current_balance = balance[
            "current_balance"
        ]

        if current_balance is None:
            continue

        try:
            update_account_balance_by_plaid_id(
                plaid_account_id=plaid_account_id,
                current_balance=current_balance,
            )

            updated_balances.append(
                {
                    "plaid_account_id": (
                        plaid_account_id
                    ),
                    "current_balance": (
                        current_balance
                    ),
                }
            )

        except ValueError:
            continue

    response = sync_transactions(
        client=client,
        access_token=access_token,
        cursor=plaid_item[
            "sync_cursor"
        ],
    )

    result = sync_plaid_transactions(
        account_id=account_id,
        added=response["added"],
        modified=response["modified"],
        removed=response["removed"],
    )

    update_plaid_cursor(
        item_id=item_id,
        sync_cursor=response[
            "next_cursor"
        ],
    )

    return {
        "account_id": account_id,
        "added": result["added"],
        "modified": result["modified"],
        "removed": result["removed"],
        "next_cursor": response[
            "next_cursor"
        ],
        "updated_balances": updated_balances,
    }