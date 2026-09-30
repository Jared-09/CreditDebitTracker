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


def test_process_same_transaction_twice_does_not_duplicate(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    first_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_duplicate_001",
        merchant_name="Test Store",
        description="Purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=True,
    )

    second_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_duplicate_001",
        merchant_name="Test Store",
        description="Purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=True,
    )

    transactions = get_all_transactions()

    assert first_transaction_id == second_transaction_id
    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[2] == "sync_duplicate_001"
    assert transaction[7] == 25.00
    assert bool(transaction[9]) is True


def test_process_pending_transaction_becoming_posted(
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
        plaid_transaction_id="sync_restaurant_pending_001",
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
    )

    posted_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_restaurant_posted_001",
        pending_transaction_id="sync_restaurant_pending_001",
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=72.00,
        pending=False,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert posted_transaction_id == pending_transaction_id
    assert transaction[0] == pending_transaction_id
    assert transaction[2] == "sync_restaurant_posted_001"
    assert transaction[7] == 72.00
    assert bool(transaction[9]) is False


def test_process_posted_transaction_when_pending_is_missing(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_missing_posted_001",
        pending_transaction_id="sync_missing_pending_001",
        merchant_name="Test Merchant",
        description="Purchase",
        transaction_date="2026-09-29",
        plaid_amount=42.50,
        pending=False,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[0] == transaction_id
    assert transaction[2] == "sync_missing_posted_001"
    assert transaction[3] == "sync_missing_pending_001"
    assert transaction[7] == 42.50
    assert bool(transaction[9]) is False