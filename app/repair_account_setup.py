from app.database import get_connection
from app.accounts import add_account


def main():
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE accounts
            SET account_role = 'other'
            WHERE id = 2
            """
        )

        connection.commit()

    finally:
        connection.close()

    connection = get_connection()

    try:
        existing = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE name = ?
              AND institution = ?
            """,
            (
                "Fairwinds Savings",
                "Fairwinds",
            ),
        ).fetchone()

    finally:
        connection.close()

    if existing is None:
        account_id = add_account(
            name="Fairwinds Savings",
            institution="Fairwinds",
            account_type="savings",
            current_balance=None,
            account_role="funding",
        )

        print(
            f"Created Fairwinds Savings "
            f"(ID {account_id})"
        )

    else:
        print(
            "Fairwinds Savings already exists "
            f"(ID {existing[0]})"
        )

    print()
    print("Account setup corrected.")


if __name__ == "__main__":
    main()