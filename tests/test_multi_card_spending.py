from app.accounting import calculate_total_spending
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
    set_manual_amount,
)


def test_calculate_spending_across_multiple_cards(test_database):
    chase_id = add_account(
        name="Freedom Flex",
        institution="Chase",
        account_type="credit_card",
        last_four="1111",
    )

    citi_id = add_account(
        name="Custom Cash",
        institution="Citi",
        account_type="credit_card",
        last_four="2222",
    )

    discover_id = add_account(
        name="Discover it",
        institution="Discover",
        account_type="credit_card",
        last_four="3333",
    )

    # Posted purchase on Chase: $40.00.
    add_transaction(
        account_id=chase_id,
        merchant_name="Grocery Store",
        description="Groceries",
        transaction_date="2026-09-30",
        plaid_amount=40.00,
        pending=False,
        plaid_transaction_id="multi_chase_001",
    )

    # Pending restaurant purchase on Citi: $65.00.
    add_transaction(
        account_id=citi_id,
        merchant_name="Restaurant",
        description="Dinner",
        transaction_date="2026-09-30",
        plaid_amount=65.00,
        pending=True,
        plaid_transaction_id="multi_citi_001",
    )

    # Discover has a $1 gas hold, but the user knows
    # the actual purchase amount is $42.50.
    gas_transaction_id = add_transaction(
        account_id=discover_id,
        merchant_name="Gas Station",
        description="Fuel",
        transaction_date="2026-09-30",
        plaid_amount=1.00,
        pending=True,
        plaid_transaction_id="multi_discover_001",
    )

    set_manual_amount(
        transaction_id=gas_transaction_id,
        manual_amount=42.50,
    )

    transactions = get_all_transactions()

    total = calculate_total_spending(transactions)

    assert total == 147.50