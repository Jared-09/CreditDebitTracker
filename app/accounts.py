from app.database import get_connection


VALID_ACCOUNT_ROLES = {
    "credit_card",
    "funding",
    "spending",
    "other",
}

UNIQUE_ACCOUNT_ROLES = {
    "funding",
    "spending",
}


def validate_account_role(account_role):
    """Reject account roles the application does not understand."""

    if account_role not in VALID_ACCOUNT_ROLES:
        raise ValueError(
            f"Invalid account role: {account_role}"
        )


def add_account(
    name,
    institution,
    account_type,
    last_four=None,
    current_balance=None,
    account_role="other",
):
    """Add an account to the database."""

    validate_account_role(account_role)

    connection = get_connection()

    try:
        if account_role in UNIQUE_ACCOUNT_ROLES:
            existing_account = connection.execute(
                """
                SELECT id
                FROM accounts
                WHERE account_role = ?
                """,
                (account_role,),
            ).fetchone()

            if existing_account is not None:
                raise ValueError(
                    f"Account role {account_role} is already assigned"
                )

        cursor = connection.execute(
            """
            INSERT INTO accounts (
                name,
                institution,
                account_type,
                last_four,
                current_balance,
                account_role
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                institution,
                account_type,
                last_four,
                current_balance,
                account_role,
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
                current_balance,
                account_role
            FROM accounts
            ORDER BY id
            """
        ).fetchall()

    finally:
        connection.close()


def get_account_by_role(account_role):
    """Return the account assigned to a specific role."""

    validate_account_role(account_role)

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
                current_balance,
                account_role
            FROM accounts
            WHERE account_role = ?
            ORDER BY id
            LIMIT 1
            """,
            (account_role,),
        ).fetchone()

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