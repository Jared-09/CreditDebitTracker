import pytest

from app.accounts import add_account
from app.database import database_transaction
from app.transactions import (
    add_transaction,
    get_all_transactions,
)


def test_shared_insert_rolls_back(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Simulate a batch that inserts a transaction,
    # then encounters an error.
    with pytest.raises(ValueError):
        with database_transaction() as connection:
            add_transaction(
                account_id=account_id,
                merchant_name="Test Gas Station",
                description="Gas purchase",
                transaction_date="2026-09-30",
                plaid_amount=40.00,
                pending=True,
                plaid_transaction_id="rollback_test_001",
                connection=connection,
            )

            # Simulate an error before the batch finishes.
            raise ValueError("Simulated batch failure")

    # The inserted transaction must not survive.
    transactions = get_all_transactions()

    assert transactions == []