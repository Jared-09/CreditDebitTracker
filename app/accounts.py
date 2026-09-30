from app.database import get_connection


def add_account(
    name,
    institution,
    account_type,
    last_four=None,
    current_balance=None,
):
    """Add an account to the database."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO accounts (
                name,
                institution,
                account_type,
                last_four,
                current_balance
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                institution,
                account_type,
                last_four,
                current_balance,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_all_accounts():
    """Return all accounts stored in the database."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                id,
                name,
                institution,
                account_type,
                last_four,
                active,
                current_balance
            FROM accounts
            ORDER BY id
            """
        ).fetchall()

    finally:
        connection.close()


def get_account_balance(account_id):
    """Return the current balance for an account."""

    connection = get_connection()

    try:
        account = connection.execute(
            """
            SELECT current_balance
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()

        if account is None:
            raise ValueError(
                f"Account {account_id} was not found."
            )

        return account[0]

    finally:
        connection.close()


def set_account_balance(
    account_id,
    current_balance,
):
    """Update the current balance for an account."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE accounts
            SET current_balance = ?
            WHERE id = ?
            """,
            (
                current_balance,
                account_id,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                f"Account {account_id} was not found."
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()