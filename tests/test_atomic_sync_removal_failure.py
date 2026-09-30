import pytest

import app.sync as sync
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_transaction_by_plaid_id,
    remove_transaction_by_plaid_id,
)


def test_plaid_sync_batch_rolls_back_after_removal_failure(
    test_database,
    monkeypatch,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Hotel",
        description="Hotel authorization",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
        plaid_transaction_id="pending_hotel_rollback_001",
    )

    def remove_then_fail(
        plaid_transaction_id,
        connection=None,
    ):
        removed = remove_transaction_by_plaid_id(
            plaid_transaction_id=plaid_transaction_id,
            connection=connection,
        )

        assert removed is True

        raise ValueError(
            "Simulated failure after removal"
        )

    monkeypatch.setattr(
        sync,
        "remove_transaction_by_plaid_id",
        remove_then_fail,
    )

    with pytest.raises(ValueError):
        sync.process_plaid_sync_batch(
            account_id=account_id,
            added=[],
            removed=[
                {
                    "plaid_transaction_id":
                        "pending_hotel_rollback_001",
                }
            ],
        )

    # The deletion occurred, but the surrounding batch failed.
    # SQLite should therefore restore the original transaction.
    original = get_transaction_by_plaid_id(
        "pending_hotel_rollback_001"
    )

    assert original is not None
    assert original[0] == transaction_id
    assert original[4] == "Test Hotel"
    assert original[7] == 100.00
    assert bool(original[9]) is True