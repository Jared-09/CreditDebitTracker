from app.accounting import calculate_remaining_liability
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
    set_manual_amount,
)


def test_calculate_remaining_liability(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Posted purchase: +$500 liability.
    add_transaction(
        account_id=account_id,
        merchant_name="Large Purchase",
        description="Posted purchase",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="liability_purchase_001",
    )

    # Pending purchase: +$100 liability.
    add_transaction(
        account_id=account_id,
        merchant_name="Pending Store",
        description="Pending purchase",
        transaction_date="2026-09-30",
        plaid_amount=100.00,
        pending=True,
        transaction_type="purchase",
        plaid_transaction_id="liability_purchase_002",
    )

    # Temporary $1 gas authorization.
    gas_transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Gas Station",
        description="Fuel authorization",
        transaction_date="2026-09-30",
        plaid_amount=1.00,
        pending=True,
        transaction_type="purchase",
        plaid_transaction_id="liability_gas_001",
    )

    # Actual expected gas purchase: +$50 liability.
    set_manual_amount(
        transaction_id=gas_transaction_id,
        manual_amount=50.00,
    )

    # Credit-card payment: -$200 liability.
    add_transaction(
        account_id=account_id,
        merchant_name="Card Payment",
        description="Payment",
        transaction_date="2026-09-30",
        plaid_amount=200.00,
        pending=False,
        transaction_type="payment",
        plaid_transaction_id="liability_payment_001",
    )

    # Refund: -$25 liability.
    add_transaction(
        account_id=account_id,
        merchant_name="Refunded Store",
        description="Refund",
        transaction_date="2026-09-30",
        plaid_amount=25.00,
        pending=False,
        transaction_type="refund",
        plaid_transaction_id="liability_refund_001",
    )

    transactions = get_all_transactions()

    remaining_liability = calculate_remaining_liability(
        transactions
    )

    assert remaining_liability == 425.00