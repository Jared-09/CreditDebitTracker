from app.database import initialize_database
from app.transactions import get_all_transactions
from app.accounting import get_effective_amount


def main():
    initialize_database()

    transactions = get_all_transactions()

    for transaction in transactions:
        plaid_amount = transaction[7]
        manual_amount = transaction[8]
        pending = transaction[9]

        effective_amount = get_effective_amount(
            plaid_amount,
            manual_amount,
            pending,
        )

        print("Plaid amount:", plaid_amount)
        print("Manual amount:", manual_amount)
        print("Pending:", bool(pending))
        print("Effective amount:", effective_amount)


if __name__ == "__main__":
    main()