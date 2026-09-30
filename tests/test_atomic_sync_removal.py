import pytest

from app.accounts import add_account
from app.sync import process_plaid_sync_batch
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
)


def test_plaid_sync_batch_rolls_back_removal(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Existing pending authorization that Plaid will remove.
    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Hotel",
        description="Hotel authorization",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
        plaid_transaction_id="pending_hotel_001",
    )

    # This modification will fail before the batch can commit.
    modified = [
        {
            "plaid_transaction_id": "missing_001",
            "merchant_name": "Missing Store",
            "description": "Should fail",
            "transaction_date": "2026-09-30",
            "plaid_amount": 50.00,
            "pending": False,
        }
    ]

    removed = [
        {
            "plaid_transaction_id": "pending_hotel_001",
        }
    ]

    with pytest.raises(ValueError):
        process_plaid_sync_batch(
            account_id=account_id,
            added=[],
            modified=modified,
            removed=removed,
        )

    # The failed batch must leave the original transaction intact.
    original = get_transaction_by_plaid_id(
        "pending_hotel_001"
    )

    assert original is not None
    assert original[0] == transaction_id
    assert original[4] == "Test Hotel"
    assert original[7] == 100.00
    assert bool(original[9]) is True