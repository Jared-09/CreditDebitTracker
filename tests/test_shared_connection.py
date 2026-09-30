from app.accounts import add_account
from app.database import database_transaction
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
)


def test_lookup_reuses_existing_connection(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-30",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="shared_connection_001",
    )

    with database_transaction() as connection:
        transaction = get_transaction_by_plaid_id(
            "shared_connection_001",
            connection=connection,
        )

        assert transaction is not None
        assert transaction[0] == transaction_id
        assert transaction[7] == 60.00

        # Verify the lookup did not close our connection.
        result = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()

        assert result[0] == 1