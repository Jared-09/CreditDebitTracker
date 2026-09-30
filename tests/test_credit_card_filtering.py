from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_credit_card_transactions,
)


def test_credit_card_transactions_exclude_non_card_accounts(
    test_database,
):
    credit_card_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    checking_id = add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="5678",
    )

    add_transaction(
        account_id=credit_card_id,
        merchant_name="Credit Card Purchase",
        description="Card purchase",
        transaction_date="2026-09-30",
        plaid_amount=100.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="filter_card_001",
    )

    add_transaction(
        account_id=checking_id,
        merchant_name="Checking Transaction",
        description="Checking account activity",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="filter_checking_001",
    )

    transactions = get_credit_card_transactions()

    assert len(transactions) == 1

    transaction = transactions[0]

    assert transaction[1] == credit_card_id
    assert transaction[2] == "filter_card_001"
    assert transaction[7] == 100.00