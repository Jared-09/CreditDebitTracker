from app.accounting import get_effective_amount
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
    get_transaction_by_plaid_id,
    mark_transaction_posted,
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