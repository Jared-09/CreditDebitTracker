from app.database import initialize_database, get_connection


def create_account(
    name,
    institution,
    account_type,
    account_role,
    current_balance,
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO accounts (
                name,
                institution,
                account_type,
                current_balance,
                account_role
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                institution,
                account_type,
                current_balance,
                account_role,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def account_exists(name):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        return row is not None

    finally:
        connection.close()


def prompt_balance(account_name):
    while True:
        value = input(
            f"Current balance for {account_name}: $"
        ).strip()

        try:
            return float(value)
        except ValueError:
            print(
                "Please enter a valid number."
            )


def main():
    initialize_database()

    print()
    print("================================")
    print("Credit Card Control Setup")
    print("================================")
    print()

    accounts = [
        {
            "name": "Amex Checking",
            "institution": "American Express",
            "account_type": "checking",
            "account_role": "funding",
        },
        {
            "name": "Fairwinds Spend Smart Checking",
            "institution": "Fairwinds",
            "account_type": "checking",
            "account_role": "spending",
        },
    ]

    for account in accounts:

        if account_exists(account["name"]):
            print(
                f"{account['name']} already exists."
            )
            continue

        balance = prompt_balance(
            account["name"]
        )

        account_id = create_account(
            name=account["name"],
            institution=account["institution"],
            account_type=account["account_type"],
            account_role=account["account_role"],
            current_balance=balance,
        )

        print(
            f"Created {account['name']} "
            f"(ID {account_id})"
        )

    print()
    print("Account setup complete.")
    print()


if __name__ == "__main__":
    main()