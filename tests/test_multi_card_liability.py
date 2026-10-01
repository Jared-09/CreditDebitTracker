from app.accounts import add_account
from app.transactions import add_transaction
from app.transactions import get_credit_card_transactions
from app.accounting import calculate_remaining_liability


def test_multiple_credit_cards_contribute_to_liability(
    test_database,
):
    card_one_id = add_account(
        name="Card One",
        institution="Test Bank",
        account_type="credit_card",
        account_role="credit_card",
    )

    card_two_id = add_account(
        name="Card Two",
        institution="Test Bank",
        account_type="credit_card",
        account_role="credit_card",
    )

    checking_id = add_account(
        name="Checking",
        institution="Test Bank",
        account_type="checking",
        account_role="spending",
    )

    add_transaction(
        account_id=card_one_id,
        merchant_name="Card One Purchase",
        description="Purchase",
        transaction_date="2026-09-30",
        plaid_amount=100.00,
        transaction_type="purchase",
        plaid_transaction_id="multi_card_001",
    )

    add_transaction(
        account_id=card_two_id,
        merchant_name="Card Two Purchase",
        description="Purchase",
        transaction_date="2026-09-30",
        plaid_amount=75.00,
        transaction_type="purchase",
        plaid_transaction_id="multi_card_002",
    )

    add_transaction(
        account_id=checking_id,
        merchant_name="Checking Purchase",
        description="Should not count",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        transaction_type="purchase",
        plaid_transaction_id="multi_card_003",
    )

    transactions = get_credit_card_transactions()

    liability = calculate_remaining_liability(
        transactions
    )

    assert liability == 175.00