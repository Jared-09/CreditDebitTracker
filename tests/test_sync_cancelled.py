from app.accounts import add_account
from app.sync import (
    process_plaid_sync_batch,
    process_plaid_transaction,
)
from app.transactions import get_all_transactions


def test_cancelled_pending_charge_removed_from_batch(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Plaid initially reports a $100 hotel authorization.
    process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="hotel_pending_001",
        merchant_name="Test Hotel",
        description="Temporary authorization",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
    )

    assert len(get_all_transactions()) == 1

    # Plaid removes the authorization without a posted charge.
    process_plaid_sync_batch(
        account_id=account_id,
        added=[],
        removed=[
            {
                "plaid_transaction_id": "hotel_pending_001",
            }
        ],
    )

    # The cancelled authorization must no longer count.
    assert get_all_transactions() == []