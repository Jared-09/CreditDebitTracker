from app.database import initialize_database
from app.plaid import (
    create_plaid_client,
    create_sandbox_public_token,
    exchange_public_token,
)
from app.plaid_items import save_plaid_item


def main():
    initialize_database()

    print()
    print("================================")
    print("Plaid Setup")
    print("================================")
    print()

    client = create_plaid_client()

    print("Creating Plaid Sandbox Item...")

    public_token = create_sandbox_public_token(
        client
    )

    print("Sandbox public token created.")

    print("Exchanging public token...")

    result = exchange_public_token(
        client=client,
        public_token=public_token,
    )

    item_id = result["item_id"]
    access_token = result["access_token"]

    print("Plaid Item created.")
    print(
        f"Item ID: {item_id}"
    )

    print("Saving Plaid Item...")

    save_plaid_item(
        item_id=item_id,
        access_token=access_token,
    )

    print("Plaid Item saved successfully.")
    print()
    print("================================")
    print("Plaid setup complete.")
    print("================================")
    print()


if __name__ == "__main__":
    main()