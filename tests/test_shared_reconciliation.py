import pytest

from app.accounts import add_account
from app.database import database_transaction
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
    reconcile_posted_transaction,
    set_manual_amount,
)


def test_shared_reconciliation_rolls_back(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Create an existing $60 pending restaurant purchase.
    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-30",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="reconcile_pending_001",
    )

    # Preserve the user's estimated final amount.
    set_manual_amount(
        transaction_id=transaction_id,
        manual_amount=72.00,
    )

    # Attempt reconciliation, then simulate a failure.
    with pytest.raises(ValueError):
        with database_transaction() as connection:
            reconciled = reconcile_posted_transaction(
                plaid_transaction_id="reconcile_posted_001",
                pending_transaction_id="reconcile_pending_001",
                posted_amount=74.00,
                connection=connection,
            )

            assert reconciled is True

            # Verify the update occurred inside the transaction.
            updated = get_transaction_by_plaid_id(
                "reconcile_posted_001",
                connection=connection,
            )

            assert updated is not None
            assert updated[7] == 74.00
            assert bool(updated[9]) is False

            raise ValueError("Simulated batch failure")

    # The rollback should restore the original pending record.
    original = get_transaction_by_plaid_id(
        "reconcile_pending_001"
    )

    assert original is not None
    assert original[0] == transaction_id
    assert original[7] == 60.00
    assert original[8] == 72.00
    assert bool(original[9]) is True

    # The posted transaction ID must not survive the rollback.
    posted = get_transaction_by_plaid_id(
        "reconcile_posted_001"
    )

    assert posted is None