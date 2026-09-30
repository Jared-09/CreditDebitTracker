from app.database import database_transaction
from app.transactions import (
    add_plaid_transaction,
    get_transaction_by_plaid_id,
    reconcile_posted_transaction,
    remove_transaction_by_plaid_id,
    update_plaid_transaction,
)


def process_plaid_transaction(
    account_id,
    plaid_transaction_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending,
    pending_transaction_id=None,
    connection=None,
):
    """Process one added transaction received from Plaid."""

    existing_transaction = get_transaction_by_plaid_id(
        plaid_transaction_id,
        connection=connection,
    )

    if existing_transaction is not None:
        return existing_transaction[0]

    if not pending and pending_transaction_id is not None:
        reconciled = reconcile_posted_transaction(
            plaid_transaction_id=plaid_transaction_id,
            pending_transaction_id=pending_transaction_id,
            posted_amount=plaid_amount,
            connection=connection,
        )

        if reconciled:
            transaction = get_transaction_by_plaid_id(
                plaid_transaction_id,
                connection=connection,
            )

            return transaction[0]

    return add_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id=plaid_transaction_id,
        merchant_name=merchant_name,
        description=description,
        transaction_date=transaction_date,
        plaid_amount=plaid_amount,
        pending=pending,
        pending_transaction_id=pending_transaction_id,
        connection=connection,
    )


def process_modified_plaid_transaction(
    plaid_transaction_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending,
    pending_transaction_id=None,
    connection=None,
):
    """Process one modified transaction received from Plaid."""

    update_plaid_transaction(
        plaid_transaction_id=plaid_transaction_id,
        merchant_name=merchant_name,
        description=description,
        transaction_date=transaction_date,
        plaid_amount=plaid_amount,
        pending=pending,
        pending_transaction_id=pending_transaction_id,
        connection=connection,
    )

    transaction = get_transaction_by_plaid_id(
        plaid_transaction_id,
        connection=connection,
    )

    return transaction[0]


def process_removed_plaid_transaction(
    plaid_transaction_id,
    connection=None,
):
    """Process one removed transaction received from Plaid."""

    return remove_transaction_by_plaid_id(
        plaid_transaction_id,
        connection=connection,
    )


def process_plaid_sync_batch(
    account_id,
    added,
    modified=None,
    removed=None,
):
    """Process one Plaid sync batch as a single database transaction."""

    if modified is None:
        modified = []

    if removed is None:
        removed = []

    transaction_ids = []

    with database_transaction() as connection:

        # Process additions first so a newly posted transaction
        # can reconcile with its existing pending transaction.
        for transaction in added:
            transaction_id = process_plaid_transaction(
                account_id=account_id,
                plaid_transaction_id=transaction[
                    "plaid_transaction_id"
                ],
                merchant_name=transaction["merchant_name"],
                description=transaction["description"],
                transaction_date=transaction[
                    "transaction_date"
                ],
                plaid_amount=transaction["plaid_amount"],
                pending=transaction["pending"],
                pending_transaction_id=transaction.get(
                    "pending_transaction_id"
                ),
                connection=connection,
            )

            transaction_ids.append(transaction_id)

        # Apply modifications using the same transaction.
        for transaction in modified:
            transaction_id = process_modified_plaid_transaction(
                plaid_transaction_id=transaction[
                    "plaid_transaction_id"
                ],
                merchant_name=transaction["merchant_name"],
                description=transaction["description"],
                transaction_date=transaction[
                    "transaction_date"
                ],
                plaid_amount=transaction["plaid_amount"],
                pending=transaction["pending"],
                pending_transaction_id=transaction.get(
                    "pending_transaction_id"
                ),
                connection=connection,
            )

            transaction_ids.append(transaction_id)

        # Process removals last. A pending transaction that was
        # reconciled above now has its posted Plaid ID, so removal
        # of the old pending ID becomes a harmless no-op.
        for transaction in removed:
            process_removed_plaid_transaction(
                plaid_transaction_id=transaction[
                    "plaid_transaction_id"
                ],
                connection=connection,
            )

    return transaction_ids