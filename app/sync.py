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
):
    """Process one added transaction received from Plaid."""

    existing_transaction = get_transaction_by_plaid_id(
        plaid_transaction_id
    )

    if existing_transaction is not None:
        return existing_transaction[0]

    if not pending and pending_transaction_id is not None:
        reconciled = reconcile_posted_transaction(
            plaid_transaction_id=plaid_transaction_id,
            pending_transaction_id=pending_transaction_id,
            posted_amount=plaid_amount,
        )

        if reconciled:
            transaction = get_transaction_by_plaid_id(
                plaid_transaction_id
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
    )


def process_modified_plaid_transaction(
    plaid_transaction_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending,
    pending_transaction_id=None,
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
    )

    transaction = get_transaction_by_plaid_id(
        plaid_transaction_id
    )

    return transaction[0]


def process_removed_plaid_transaction(plaid_transaction_id):
    """Process one removed transaction received from Plaid."""

    return remove_transaction_by_plaid_id(
        plaid_transaction_id
    )


def process_plaid_sync_batch(
    account_id,
    added,
    modified=None,
    removed=None,
):
    """Process added, modified, and removed Plaid transactions."""

    if modified is None:
        modified = []

    if removed is None:
        removed = []

    transaction_ids = []

    # Process added transactions first so posted purchases
    # can reconcile with their existing pending records.
    for transaction in added:
        transaction_id = process_plaid_transaction(
            account_id=account_id,
            plaid_transaction_id=transaction["plaid_transaction_id"],
            merchant_name=transaction["merchant_name"],
            description=transaction["description"],
            transaction_date=transaction["transaction_date"],
            plaid_amount=transaction["plaid_amount"],
            pending=transaction["pending"],
            pending_transaction_id=transaction.get(
                "pending_transaction_id"
            ),
        )

        transaction_ids.append(transaction_id)

    # Apply updates to existing transactions.
    for transaction in modified:
        transaction_id = process_modified_plaid_transaction(
            plaid_transaction_id=transaction["plaid_transaction_id"],
            merchant_name=transaction["merchant_name"],
            description=transaction["description"],
            transaction_date=transaction["transaction_date"],
            plaid_amount=transaction["plaid_amount"],
            pending=transaction["pending"],
            pending_transaction_id=transaction.get(
                "pending_transaction_id"
            ),
        )

        transaction_ids.append(transaction_id)

    # Process removals last. If an old pending transaction
    # was reconciled above, its old Plaid ID no longer exists,
    # so removing that ID will not delete the posted purchase.
    for transaction in removed:
        process_removed_plaid_transaction(
            plaid_transaction_id=transaction["plaid_transaction_id"]
        )

    return transaction_ids