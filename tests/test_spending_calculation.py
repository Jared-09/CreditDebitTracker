from app.accounting import calculate_total_spending
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
    set_manual_amount,
)


def test_calculate_total_effective_spending(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Normal posted purchase: counts as $25.00.
    add_transaction(
        account_id=account_id,
        merchant_name="Grocery Store",
        description="Groceries",
        transaction_date="2026-09-30",
        plaid_amount=25.00,
        pending=False,
        plaid_transaction_id="spending_posted_001",
    )

    # Pending restaurant purchase with no override:
    # counts as the current Plaid amount of $60.00.
    add_transaction(
        account_id=account_id,
        merchant_name="Restaurant",
        description="Dinner",
        transaction_date="2026-09-30",
        plaid_amount=60.00,
        pending=True,
        plaid_transaction_id="spending_pending_001",
    )

    # Gas station places a temporary $1 hold.
    gas_transaction_id = add_transaction(
        account_id=account_id,
        merchant_name="Gas Station",
        description="Fuel",
        transaction_date="2026-09-30",
        plaid_amount=1.00,
        pending=True,
        plaid_transaction_id="spending_gas_001",
    )

    # User knows the actual purchase was $47.36.
    set_manual_amount(
        transaction_id=gas_transaction_id,
        manual_amount=47.36,
    )

    # A non-purchase transaction should not count toward spending.
    add_transaction(
        account_id=account_id,
        merchant_name="Card Payment",
        description="Credit card payment",
        transaction_date="2026-09-30",
        plaid_amount=100.00,
        pending=False,
        transaction_type="payment",
        plaid_transaction_id="spending_payment_001",
    )

    transactions = get_all_transactions()

    total = calculate_total_spending(transactions)

    assert total == 132.36