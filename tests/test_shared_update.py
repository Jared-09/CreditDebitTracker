import pytest

from app.accounts import add_account
from app.database import database_transaction
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
    update_plaid_transaction,
)


def test_shared_update_rolls_back(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Create an existing $60 transaction.
    add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-30",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="rollback_update_001",
    )

    # Simulate a Plaid batch updating the amount,
    # followed by an unexpected failure.
    with pytest.raises(ValueError):
        with database_transaction() as connection:
            update_plaid_transaction(
                plaid_transaction_id="rollback_update_001",
                merchant_name="Test Restaurant",
                description="Dinner with tip",
                transaction_date="2026-09-30",
                plaid_amount=72.00,
                pending=False,
                connection=connection,
            )

            raise ValueError("Simulated batch failure")

    # Verify that the original transaction was restored.
    transaction = get_transaction_by_plaid_id(
        "rollback_update_001"
    )

    assert transaction is not None
    assert transaction[7] == 60.00
    assert bool(transaction[9]) is True
    assert transaction[5] == "Dinner"