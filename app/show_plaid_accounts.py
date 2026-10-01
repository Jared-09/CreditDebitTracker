from app.database import initialize_database, get_connection

from app.plaid import (
    create_plaid_client,
    get_plaid_account_balances,
)


def get_latest_plaid_item():
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                item_id,
                access_token
            FROM plaid_items
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return None

        return {
            "item_id": row[0],
            "access_token": row[1],
        }

    finally:
        connection.close()


def main():
    initialize_database()

    print()
    print("================================")
    print("Plaid Account Discovery")
    print("================================")
    print()

    item = get_latest_plaid_item()

    if item is None:
        print("No saved Plaid Item found.")
        return

    print(
        f"Using newest Plaid Item: "
        f"{item['item_id']}"
    )
    print()

    client = create_plaid_client()

    accounts = get_plaid_account_balances(
        client=client,
        access_token=item["access_token"],
    )

    if not accounts:
        print("Plaid returned no accounts.")
        return

    for account in accounts:
        print(
            f"Plaid Account ID: "
            f"{account['plaid_account_id']}"
        )

        print(
            f"Name: "
            f"{account['name']}"
        )

        print(
            f"Official Name: "
            f"{account['official_name']}"
        )

        print(
            f"Type: "
            f"{account['account_type']}"
        )

        print(
            f"Subtype: "
            f"{account['account_subtype']}"
        )

        print(
            f"Current Balance: "
            f"${account['current_balance']}"
        )

        print(
            f"Available Balance: "
            f"${account['available_balance']}"
        )

        print("--------------------------------")

    print()
    print("Discovery complete.")


if __name__ == "__main__":
    main()