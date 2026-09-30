from app.database import get_connection


def add_transaction(
    account_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending=False,
    transaction_type="purchase",
    plaid_transaction_id=None,
    pending_transaction_id=None,
):
    """Add a transaction to the database."""
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO transactions (
            account_id,
            plaid_transaction_id,
            pending_transaction_id,
            merchant_name,
            description,
            transaction_date,
            plaid_amount,
            pending,
            transaction_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            account_id,
            plaid_transaction_id,
            pending_transaction_id,
            merchant_name,
            description,
            transaction_date,
            plaid_amount,
            int(pending),
            transaction_type,
        ),
    )

    connection.commit()

    transaction_id = cursor.lastrowid

    connection.close()

    return transaction_id


def get_all_transactions():
    """Return all transactions stored in the database."""
    connection = get_connection()

    transactions = connection.execute(
        """
        SELECT
            id,
            account_id,
            plaid_transaction_id,
            pending_transaction_id,
            merchant_name,
            description,
            transaction_date,
            plaid_amount,
            manual_amount,
            pending,
            transaction_type
        FROM transactions
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return transactions


def get_transaction_by_plaid_id(plaid_transaction_id):
    """Return a transaction with the given Plaid transaction ID."""
    connection = get_connection()

    transaction = connection.execute(
        """
        SELECT
            id,
            account_id,
            plaid_transaction_id,
            pending_transaction_id,
            merchant_name,
            description,
            transaction_date,
            plaid_amount,
            manual_amount,
            pending,
            transaction_type
        FROM transactions
        WHERE plaid_transaction_id = ?
        """,
        (plaid_transaction_id,),
    ).fetchone()

    connection.close()

    return transaction


def add_plaid_transaction(
    account_id,
    plaid_transaction_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending=False,
    transaction_type="purchase",
    pending_transaction_id=None,
):
    """Add a Plaid transaction only if it is not already stored."""

    existing_transaction = get_transaction_by_plaid_id(
        plaid_transaction_id
    )

    if existing_transaction is not None:
        return existing_transaction[0]

    return add_transaction(
        account_id=account_id,
        merchant_name=merchant_name,
        description=description,
        transaction_date=transaction_date,
        plaid_amount=plaid_amount,
        pending=pending,
        transaction_type=transaction_type,
        plaid_transaction_id=plaid_transaction_id,
        pending_transaction_id=pending_transaction_id,
    )


def update_plaid_transaction(
    plaid_transaction_id,
    merchant_name,
    description,
    transaction_date,
    plaid_amount,
    pending,
    pending_transaction_id=None,
):
    """Update an existing transaction using current Plaid data."""
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE transactions
        SET
            pending_transaction_id = ?,
            merchant_name = ?,
            description = ?,
            transaction_date = ?,
            plaid_amount = ?,
            pending = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE plaid_transaction_id = ?
        """,
        (
            pending_transaction_id,
            merchant_name,
            description,
            transaction_date,
            plaid_amount,
            int(pending),
            plaid_transaction_id,
        ),
    )

    if cursor.rowcount != 1:
        connection.close()
        raise ValueError(
            f"Plaid transaction {plaid_transaction_id} was not found."
        )

    connection.commit()
    connection.close()


def set_manual_amount(transaction_id, manual_amount):
    """Set a manual amount override for a transaction."""
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE transactions
        SET
            manual_amount = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (manual_amount, transaction_id),
    )

    if cursor.rowcount != 1:
        connection.close()
        raise ValueError(f"Transaction {transaction_id} was not found.")

    connection.commit()
    connection.close()


def mark_transaction_posted(
    transaction_id,
    posted_amount,
    plaid_transaction_id=None,
):
    """Update a pending transaction when its final posted amount becomes known."""
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE transactions
        SET
            plaid_amount = ?,
            plaid_transaction_id = COALESCE(?, plaid_transaction_id),
            pending = 0,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            posted_amount,
            plaid_transaction_id,
            transaction_id,
        ),
    )

    if cursor.rowcount != 1:
        connection.close()
        raise ValueError(f"Transaction {transaction_id} was not found.")

    connection.commit()
    connection.close()


def reconcile_posted_transaction(
    plaid_transaction_id,
    pending_transaction_id,
    posted_amount,
):
    """Reconcile a posted Plaid transaction with its earlier pending transaction."""

    pending_transaction = get_transaction_by_plaid_id(
        pending_transaction_id
    )

    if pending_transaction is None:
        return False

    transaction_id = pending_transaction[0]

    mark_transaction_posted(
        transaction_id=transaction_id,
        posted_amount=posted_amount,
        plaid_transaction_id=plaid_transaction_id,
    )

    return True


def remove_transaction_by_plaid_id(plaid_transaction_id):
    """Remove a transaction using its Plaid transaction ID."""
    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM transactions
        WHERE plaid_transaction_id = ?
        """,
        (plaid_transaction_id,),
    )

    connection.commit()

    removed = cursor.rowcount == 1

    connection.close()

    return removed