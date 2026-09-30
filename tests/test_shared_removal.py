import pytest

from app.accounts import add_account
from app.database import database_transaction
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
    remove_transaction_by_plaid_id,
)


def test_shared_removal_rolls_back(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Create an existing $100 pending authorization.
    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Hotel",
        description="Temporary authorization",
        transaction_date="2026-09-30",
        plaid_amount=100.00,
        pending=True,
        plaid_transaction_id="rollback_removal_001",
    )

    # Simulate removing the transaction, then encountering an error.
    with pytest.raises(ValueError):
        with database_transaction() as connection:
            removed = remove_transaction_by_plaid_id(
                plaid_transaction_id="rollback_removal_001",
                connection=connection,
            )

            assert removed is True

            # Simulate a failure before the batch finishes.
            raise ValueError("Simulated batch failure")

    # The transaction should still exist after rollback.
    transaction = get_transaction_by_plaid_id(
        "rollback_removal_001"
    )

    assert transaction is not None
    assert transaction[0] == transaction_id
    assert transaction[7] == 100.00
    assert bool(transaction[9]) is True