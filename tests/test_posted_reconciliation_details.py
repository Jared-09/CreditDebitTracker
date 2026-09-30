from app.accounts import add_account
from app.sync import process_plaid_transaction
from app.transactions import (
    get_transaction_by_plaid_id,
    set_manual_amount,
)


def test_posted_reconciliation_updates_final_details(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    pending_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="pending_details_001",
        merchant_name="SQ *RESTAURANT",
        description="Pending restaurant authorization",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
    )

    # Preserve a manual estimate while the transaction is pending.
    set_manual_amount(
        transaction_id=pending_transaction_id,
        manual_amount=72.00,
    )

    posted_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="posted_details_001",
        pending_transaction_id="pending_details_001",
        merchant_name="Example Restaurant",
        description="Restaurant purchase",
        transaction_date="2026-09-30",
        plaid_amount=71.84,
        pending=False,
    )

    # Reconciliation should reuse the original database row.
    assert posted_transaction_id == pending_transaction_id

    transaction = get_transaction_by_plaid_id(
        "posted_details_001"
    )

    assert transaction is not None

    # Final Plaid details should replace the preliminary pending details.
    assert transaction[4] == "Example Restaurant"
    assert transaction[5] == "Restaurant purchase"
    assert transaction[6] == "2026-09-30"

    # Final posted amount becomes authoritative.
    assert transaction[7] == 71.84
    assert bool(transaction[9]) is False

    # Manual history is preserved rather than erased.
    assert transaction[8] == 72.00