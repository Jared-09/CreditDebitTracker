import pytest

from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
)


def test_valid_transaction_types_are_accepted(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    valid_types = (
        "purchase",
        "payment",
        "refund",
    )

    for number, transaction_type in enumerate(
        valid_types
    ):
        add_transaction(
            account_id=account_id,
            merchant_name="Test Merchant",
            description="Valid transaction type",
            transaction_date="2026-09-30",
            plaid_amount=10.00,
            pending=False,
            transaction_type=transaction_type,
            plaid_transaction_id=(
                f"valid_type_{number}"
            ),
        )

    transactions = get_all_transactions()

    assert len(transactions) == 3

    stored_types = {
        transaction[10]
        for transaction in transactions
    }

    assert stored_types == {
        "purchase",
        "payment",
        "refund",
    }


def test_invalid_transaction_type_is_rejected(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    with pytest.raises(
        ValueError,
        match="Invalid transaction type",
    ):
        add_transaction(
            account_id=account_id,
            merchant_name="Test Merchant",
            description="Invalid classification",
            transaction_date="2026-09-30",
            plaid_amount=500.00,
            pending=False,
            transaction_type="puchase",
            plaid_transaction_id="invalid_type_001",
        )

    # The rejected transaction must never reach the database.
    transactions = get_all_transactions()

    assert transactions == []