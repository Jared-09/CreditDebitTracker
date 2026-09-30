from app.accounting import (
    calculate_remaining_liability,
    calculate_total_spending,
    calculate_transfer_needed,
)
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
)


def test_repeated_small_purchases_are_exact(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    for number in range(3):
        add_transaction(
            account_id=account_id,
            merchant_name="Small Purchase",
            description="Ten cent purchase",
            transaction_date="2026-09-30",
            plaid_amount=0.10,
            pending=False,
            transaction_type="purchase",
            plaid_transaction_id=f"precision_010_{number}",
        )

    transactions = get_all_transactions()

    assert calculate_total_spending(transactions) == 0.30
    assert calculate_remaining_liability(transactions) == 0.30


def test_many_cent_transactions_are_exact(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    for number in range(100):
        add_transaction(
            account_id=account_id,
            merchant_name="Small Purchase",
            description="One cent purchase",
            transaction_date="2026-09-30",
            plaid_amount=0.01,
            pending=False,
            transaction_type="purchase",
            plaid_transaction_id=f"precision_001_{number}",
        )

    transactions = get_all_transactions()

    assert calculate_total_spending(transactions) == 1.00
    assert calculate_remaining_liability(transactions) == 1.00


def test_transfer_calculation_uses_cent_precision():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=0.30,
        ap_balance=0.10,
    )

    assert transfer_needed == 0.20


def test_money_rounds_half_up_to_cents():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=10.005,
        ap_balance=0.00,
    )

    assert transfer_needed == 10.01