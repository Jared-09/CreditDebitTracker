from app.accounts import add_account
from app.sync import process_plaid_transaction
from app.transactions import get_all_transactions


def test_process_new_pending_transaction(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_pending_001",
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[0] == transaction_id
    assert transaction[2] == "sync_pending_001"
    assert transaction[4] == "Test Restaurant"
    assert transaction[7] == 60.00
    assert bool(transaction[9]) is True