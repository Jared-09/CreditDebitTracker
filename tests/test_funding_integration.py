from app.accounting import (
    calculate_remaining_liability,
    calculate_transfer_needed,
)
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
)


def test_card_payment_preserves_funding_shortage(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Total purchases = $650.
    add_transaction(
        account_id=account_id,
        merchant_name="Purchase One",
        description="First purchase",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="funding_purchase_001",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Purchase Two",
        description="Second purchase",
        transaction_date="2026-09-30",
        plaid_amount=150.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="funding_purchase_002",
    )

    transactions = get_all_transactions()

    liability_before_payment = calculate_remaining_liability(
        transactions
    )

    ap_balance_before_payment = 500.00

    transfer_before_payment = calculate_transfer_needed(
        remaining_liability=liability_before_payment,
        ap_balance=ap_balance_before_payment,
    )

    assert liability_before_payment == 650.00
    assert transfer_before_payment == 150.00

    # Pay $300 toward the card using money from Fairwinds AP.
    add_transaction(
        account_id=account_id,
        merchant_name="Card Payment",
        description="Payment from Fairwinds AP",
        transaction_date="2026-09-30",
        plaid_amount=300.00,
        pending=False,
        transaction_type="payment",
        plaid_transaction_id="funding_payment_001",
    )

    transactions = get_all_transactions()

    liability_after_payment = calculate_remaining_liability(
        transactions
    )

    # The same $300 payment also leaves Fairwinds AP.
    ap_balance_after_payment = 200.00

    transfer_after_payment = calculate_transfer_needed(
        remaining_liability=liability_after_payment,
        ap_balance=ap_balance_after_payment,
    )

    assert liability_after_payment == 350.00
    assert transfer_after_payment == 150.00

    # Paying the card from AP must not create a new funding shortage.
    assert transfer_after_payment == transfer_before_payment