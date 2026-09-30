from app.accounts import add_account
from app.sync import (
    process_plaid_sync_batch,
    process_plaid_transaction,
)
from app.transactions import (
    get_all_transactions,
    set_manual_amount,
)


def test_pending_to_posted_with_removal(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Step 1: Plaid initially reports a $60 pending purchase.
    original_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="restaurant_pending_001",
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
    )

    # Step 2: The user estimates a $72 final total.
    set_manual_amount(
        transaction_id=original_id,
        manual_amount=72.00,
    )

    # Step 3: Plaid reports the posted transaction
    # and removes the original pending transaction.
    added = [
        {
            "plaid_transaction_id": "restaurant_posted_001",
            "pending_transaction_id": "restaurant_pending_001",
            "merchant_name": "Test Restaurant",
            "description": "Dinner with tip",
            "transaction_date": "2026-09-30",
            "plaid_amount": 72.00,
            "pending": False,
        },
    ]

    removed = [
        {
            "plaid_transaction_id": "restaurant_pending_001",
        },
    ]

    process_plaid_sync_batch(
        account_id=account_id,
        added=added,
        removed=removed,
    )

    # Step 4: Verify the final database state.
    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    # Original database record was preserved.
    assert transaction[0] == original_id

    # New posted Plaid ID replaced the pending ID.
    assert transaction[2] == "restaurant_posted_001"

    # Final posted amount is correct.
    assert transaction[7] == 72.00

    # Manual estimate remains stored for reference.
    assert transaction[8] == 72.00

    # Transaction is no longer pending.
    assert bool(transaction[9]) is False