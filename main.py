from app.database import initialize_database

from app.plaid import (
    create_plaid_client,
)

from app.plaid_sync_all import (
    sync_all_plaid_accounts,
)

from app.reporting import (
    print_daily_report,
)


def main():

    initialize_database()

    print()
    print("================================")
    print("Credit Card Control")
    print("================================")
    print()

    print("Syncing accounts...")

    client = create_plaid_client()

    results = sync_all_plaid_accounts(
        client
    )

    print(
        f"Synced accounts: {len(results)}"
    )

    print()

    print_daily_report()


if __name__ == "__main__":
    main()