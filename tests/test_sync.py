from app.accounts import add_account
from app.sync import (
    process_modified_plaid_transaction,
    process_plaid_sync_batch,
    process_plaid_transaction,
    process_removed_plaid_transaction,
)
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


def test_process_modified_plaid_transaction(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    original_transaction_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_modified_001",
        merchant_name="Test Store",
        description="Purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=False,
    )

    modified_transaction_id = process_modified_plaid_transaction(
        plaid_transaction_id="sync_modified_001",
        merchant_name="Test Store",
        description="Updated purchase",
        transaction_date="2026-09-29",
        plaid_amount=27.50,
        pending=False,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert modified_transaction_id == original_transaction_id
    assert transaction[0] == original_transaction_id
    assert transaction[2] == "sync_modified_001"
    assert transaction[5] == "Updated purchase"
    assert transaction[7] == 27.50
    assert bool(transaction[9]) is False


def test_process_removed_plaid_transaction(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="sync_removed_001",
        merchant_name="Test Hotel",
        description="Authorization hold",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1
    assert transactions[0][7] == 100.00

    removed = process_removed_plaid_transaction(
        plaid_transaction_id="sync_removed_001"
    )

    assert removed is True
    assert get_all_transactions() == []


def test_process_plaid_sync_batch_with_added_transactions(
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
            "plaid_transaction_id": "batch_added_001",
            "merchant_name": "Test Restaurant",
            "description": "Lunch",
            "transaction_date": "2026-09-29",
            "plaid_amount": 12.00,
            "pending": False,
        },
        {
            "plaid_transaction_id": "batch_added_002",
            "merchant_name": "Test Gas Station",
            "description": "Gas",
            "transaction_date": "2026-09-29",
            "plaid_amount": 40.00,
            "pending": True,
        },
        {
            "plaid_transaction_id": "batch_added_003",
            "merchant_name": "Test Store",
            "description": "Purchase",
            "transaction_date": "2026-09-29",
            "plaid_amount": 25.00,
            "pending": False,
        },
    ]

    transaction_ids = process_plaid_sync_batch(
        account_id=account_id,
        added=added,
    )

    transactions = get_all_transactions()

    assert len(transaction_ids) == 3
    assert len(transactions) == 3

    assert transactions[0][2] == "batch_added_001"
    assert transactions[0][7] == 12.00
    assert bool(transactions[0][9]) is False

    assert transactions[1][2] == "batch_added_002"
    assert transactions[1][7] == 40.00
    assert bool(transactions[1][9]) is True

    assert transactions[2][2] == "batch_added_003"
    assert transactions[2][7] == 25.00
    assert bool(transactions[2][9]) is False