import pytest

from app.accounts import add_account
from app.sync import process_plaid_sync_batch
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
    set_manual_amount,
)


def test_plaid_sync_batch_rolls_back_reconciliation(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Original pending restaurant transaction.
    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="restaurant_pending_001",
    )

    # User estimates the final total including tip at $72.
    set_manual_amount(
        transaction_id=transaction_id,
        manual_amount=72.00,
    )

    added = [
        {
            # Plaid replaces the pending transaction with
            # a new posted transaction ID and final amount.
            "plaid_transaction_id": "restaurant_posted_001",
            "pending_transaction_id": "restaurant_pending_001",
            "merchant_name": "Test Restaurant",
            "description": "Dinner",
            "transaction_date": "2026-09-30",
            "plaid_amount": 74.00,
            "pending": False,
        }
    ]

    modified = [
        {
            # Force a failure after reconciliation has occurred.
            "plaid_transaction_id": "missing_transaction_001",
            "merchant_name": "Missing Store",
            "description": "Should fail",
            "transaction_date": "2026-09-30",
            "plaid_amount": 25.00,
            "pending": False,
        }
    ]

    with pytest.raises(ValueError):
        process_plaid_sync_batch(
            account_id=account_id,
            added=added,
            modified=modified,
        )

    # The original pending transaction must be restored.
    original = get_transaction_by_plaid_id(
        "restaurant_pending_001"
    )

    assert original is not None
    assert original[0] == transaction_id
    assert original[7] == 60.00
    assert original[8] == 72.00
    assert bool(original[9]) is True

    # The new posted Plaid ID must not survive the rollback.
    posted = get_transaction_by_plaid_id(
        "restaurant_posted_001"
    )

    assert posted is None