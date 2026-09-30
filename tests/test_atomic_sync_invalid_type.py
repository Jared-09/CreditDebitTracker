import pytest

from app.accounts import add_account
from app.sync import process_plaid_sync_batch
from app.transactions import get_all_transactions


def test_invalid_transaction_type_rolls_back_entire_sync_batch(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    added = [
        {
            "plaid_transaction_id": "valid_batch_001",
            "merchant_name": "Valid Merchant",
            "description": "Valid purchase",
            "transaction_date": "2026-09-30",
            "plaid_amount": 40.00,
            "pending": False,
            "transaction_type": "purchase",
        },
        {
            "plaid_transaction_id": "invalid_batch_001",
            "merchant_name": "Invalid Merchant",
            "description": "Bad classification",
            "transaction_date": "2026-09-30",
            "plaid_amount": 500.00,
            "pending": False,
            "transaction_type": "puchase",
        },
    ]

    with pytest.raises(
        ValueError,
        match="Invalid transaction type",
    ):
        process_plaid_sync_batch(
            account_id=account_id,
            added=added,
        )

    # The valid first transaction must also be rolled back.
    # A sync batch is all-or-nothing.
    transactions = get_all_transactions()

    assert transactions == []