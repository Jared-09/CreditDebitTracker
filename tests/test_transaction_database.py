from app.accounting import get_effective_amount
from app.accounts import add_account
from app.transactions import (
    add_plaid_transaction,
    add_transaction,
    get_all_transactions,
    get_transaction_by_plaid_id,
    mark_transaction_posted,
    reconcile_posted_transaction,
    remove_transaction_by_plaid_id,
    set_manual_amount,
)


def test_pending_gas_transaction_lifecycle(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Gas Station",
        description="Gas authorization",
        transaction_date="2026-09-29",
        plaid_amount=1.00,
        pending=True,
        plaid_transaction_id="test_pending_gas_001",
    )

    set_manual_amount(
        transaction_id=transaction_id,
        manual_amount=47.36,
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[7] == 1.00
    assert transaction[8] == 47.36
    assert bool(transaction[9]) is True

    pending_effective_amount = get_effective_amount(
        plaid_amount=transaction[7],
        manual_amount=transaction[8],
        pending=transaction[9],
    )

    assert pending_effective_amount == 47.36

    mark_transaction_posted(
        transaction_id=transaction_id,
        posted_amount=48.10,
        plaid_transaction_id="test_posted_gas_001",
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[2] == "test_posted_gas_001"
    assert transaction[7] == 48.10
    assert transaction[8] == 47.36
    assert bool(transaction[9]) is False

    posted_effective_amount = get_effective_amount(
        plaid_amount=transaction[7],
        manual_amount=transaction[8],
        pending=transaction[9],
    )

    assert posted_effective_amount == 48.10


def test_get_transaction_by_plaid_id(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="test_restaurant_001",
    )

    transaction = get_transaction_by_plaid_id("test_restaurant_001")

    assert transaction is not None
    assert transaction[0] == transaction_id
    assert transaction[2] == "test_restaurant_001"
    assert transaction[4] == "Test Restaurant"
    assert transaction[7] == 60.00

    missing_transaction = get_transaction_by_plaid_id(
        "this_id_does_not_exist"
    )

    assert missing_transaction is None


def test_reconcile_pending_restaurant_transaction(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Test Restaurant",
        description="Dinner",
        transaction_date="2026-09-29",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="pending_restaurant_001",
    )

    reconciled = reconcile_posted_transaction(
        plaid_transaction_id="posted_restaurant_001",
        pending_transaction_id="pending_restaurant_001",
        posted_amount=72.00,
    )

    assert reconciled is True

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[2] == "posted_restaurant_001"
    assert transaction[7] == 72.00
    assert bool(transaction[9]) is False


def test_remove_cancelled_pending_transaction(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Test Hotel",
        description="Authorization hold",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
        plaid_transaction_id="pending_cancelled_001",
    )

    transactions = get_all_transactions()

    assert len(transactions) == 1
    assert transactions[0][7] == 100.00
    assert bool(transactions[0][9]) is True

    removed = remove_transaction_by_plaid_id(
        "pending_cancelled_001"
    )

    assert removed is True
    assert get_all_transactions() == []

    removed_again = remove_transaction_by_plaid_id(
        "pending_cancelled_001"
    )

    assert removed_again is False


def test_reconcile_pending_transaction_with_lower_posted_amount(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Test Merchant",
        description="Pending authorization",
        transaction_date="2026-09-29",
        plaid_amount=100.00,
        pending=True,
        plaid_transaction_id="pending_lower_001",
    )

    transaction = get_all_transactions()[0]

    pending_effective_amount = get_effective_amount(
        plaid_amount=transaction[7],
        manual_amount=transaction[8],
        pending=transaction[9],
    )

    assert pending_effective_amount == 100.00

    reconciled = reconcile_posted_transaction(
        plaid_transaction_id="posted_lower_001",
        pending_transaction_id="pending_lower_001",
        posted_amount=85.00,
    )

    assert reconciled is True

    transactions = get_all_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    posted_effective_amount = get_effective_amount(
        plaid_amount=transaction[7],
        manual_amount=transaction[8],
        pending=transaction[9],
    )

    assert transaction[2] == "posted_lower_001"
    assert transaction[7] == 85.00
    assert bool(transaction[9]) is False
    assert posted_effective_amount == 85.00


def test_duplicate_plaid_transaction_is_not_added_twice(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    first_transaction_id = add_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="duplicate_test_001",
        merchant_name="Test Store",
        description="Test purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=False,
    )

    second_transaction_id = add_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="duplicate_test_001",
        merchant_name="Test Store",
        description="Test purchase",
        transaction_date="2026-09-29",
        plaid_amount=25.00,
        pending=False,
    )

    transactions = get_all_transactions()

    assert first_transaction_id == second_transaction_id
    assert len(transactions) == 1
    assert transactions[0][2] == "duplicate_test_001"
    assert transactions[0][7] == 25.00