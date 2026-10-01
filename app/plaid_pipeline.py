from app.accounts import (
    get_account_by_plaid_account_id,
)

from app.plaid import (
    convert_plaid_transaction,
)

from app.sync import (
    process_plaid_transaction,
    process_modified_plaid_transaction,
    process_removed_plaid_transaction,
)


def sync_plaid_transactions(
    account_id,
    added,
    modified,
    removed,
):
    """
    Process Plaid transaction changes into the
    application's transaction database.

    Each Plaid transaction is assigned to the local
    account associated with its Plaid account ID.
    """

    added_count = 0
    modified_count = 0
    removed_count = 0

    for transaction in added:
        converted = convert_plaid_transaction(
            transaction
        )

        plaid_account_id = transaction.get(
            "account_id"
        )

        local_account_id = None

        if plaid_account_id is not None:
            local_account_id = (
                get_account_by_plaid_account_id(
                    plaid_account_id
                )
            )

        if local_account_id is None:
            local_account_id = account_id

        process_plaid_transaction(
            account_id=local_account_id,
            plaid_transaction_id=converted[
                "plaid_transaction_id"
            ],
            pending_transaction_id=converted.get(
                "pending_transaction_id"
            ),
            merchant_name=converted[
                "merchant_name"
            ],
            description=converted[
                "description"
            ],
            transaction_date=converted[
                "transaction_date"
            ],
            plaid_amount=converted[
                "plaid_amount"
            ],
            pending=converted[
                "pending"
            ],
            transaction_type=converted[
                "transaction_type"
            ],
        )

        added_count += 1

    for transaction in modified:
        converted = convert_plaid_transaction(
            transaction
        )

        process_modified_plaid_transaction(
            plaid_transaction_id=converted[
                "plaid_transaction_id"
            ],
            merchant_name=converted[
                "merchant_name"
            ],
            description=converted[
                "description"
            ],
            transaction_date=converted[
                "transaction_date"
            ],
            plaid_amount=converted[
                "plaid_amount"
            ],
            pending=converted[
                "pending"
            ],
            transaction_type=converted[
                "transaction_type"
            ],
        )

        modified_count += 1

    for transaction_id in removed:
        process_removed_plaid_transaction(
            plaid_transaction_id=transaction_id
        )

        removed_count += 1

    return {
        "added": added_count,
        "modified": modified_count,
        "removed": removed_count,
    }