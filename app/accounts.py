from app.database import get_connection


def add_account(name, institution, account_type, last_four=None):
    """Add an account to the database."""
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO accounts (
            name,
            institution,
            account_type,
            last_four
        )
        VALUES (?, ?, ?, ?)
        """,
        (name, institution, account_type, last_four),
    )

    connection.commit()

    account_id = cursor.lastrowid

    connection.close()

    return account_id

def get_all_accounts():
    """Return all accounts stored in the database."""
    connection = get_connection()

    accounts = connection.execute(
        """
        SELECT
            id,
            name,
            institution,
            account_type,
            last_four,
            active
        FROM accounts
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return accounts