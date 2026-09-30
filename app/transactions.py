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

def set_manual_amount(transaction_id, manual_amount):
    """Set a manual amount override for a transaction."""
    connection = get_connection()

    connection.execute(
        """
        UPDATE transactions
        SET
            manual_amount = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (manual_amount, transaction_id),
    )

    connection.commit()
    connection.close()