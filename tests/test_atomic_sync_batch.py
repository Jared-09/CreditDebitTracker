import pytest

from app.accounts import add_account
from app.sync import process_plaid_sync_batch
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
)


def test_plaid_sync_batch_rolls_back_everything(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Existing transaction that the batch will successfully modify.
    add_transaction(
        account_id=account_id,
        merchant_name="Original Store",
        description="Original purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=True,
        plaid_transaction_id="existing_001",
    )

    added = [
        {
            "plaid_transaction_id": "new_001",
            "merchant_name": "Coffee Shop",
            "description": "Coffee",
            "transaction_date": "2026-09-30",
            "plaid_amount": 8.50,
            "pending": True,
        }
    ]

    modified = [
        {
            "plaid_transaction_id": "existing_001",
            "merchant_name": "Updated Store",
            "description": "Updated purchase",
            "transaction_date": "2026-09-30",
            "plaid_amount": 30.00,
            "pending": False,
        },
        {
            # This transaction does not exist.
            # Its update will raise ValueError and force
            # the entire database transaction to roll back.
            "plaid_transaction_id": "missing_001",
            "merchant_name": "Missing Store",
            "description": "Should fail",
            "transaction_date": "2026-09-30",
            "plaid_amount": 40.00,
            "pending": False,
        },
    ]

    with pytest.raises(ValueError):
        process_plaid_sync_batch(
            account_id=account_id,
            added=added,
            modified=modified,
        )

    # The successfully added transaction must have been rolled back.
    new_transaction = get_transaction_by_plaid_id(
        "new_001"
    )

    assert new_transaction is None

    # The earlier modification must also have been rolled back.
    original_transaction = get_transaction_by_plaid_id(
        "existing_001"
    )

    assert original_transaction is not None
    assert original_transaction[4] == "Original Store"
    assert original_transaction[5] == "Original purchase"
    assert original_transaction[6] == "2026-09-29"
    assert original_transaction[7] == 25.00
    assert bool(original_transaction[9]) is True