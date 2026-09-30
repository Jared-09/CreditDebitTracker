from app.accounts import add_account
from app.sync import (
    process_modified_plaid_transaction,
    process_plaid_transaction,
)
from app.transactions import get_transaction_by_plaid_id


def test_modified_transaction_can_update_transaction_type(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="modified_type_001",
        merchant_name="Example Merchant",
        description="Original transaction",
        transaction_date="2026-09-29",
        plaid_amount=50.00,
        pending=False,
        transaction_type="purchase",
    )

    process_modified_plaid_transaction(
        plaid_transaction_id="modified_type_001",
        merchant_name="Example Merchant",
        description="Corrected refund",
        transaction_date="2026-09-30",
        plaid_amount=50.00,
        pending=False,
        transaction_type="refund",
    )

    transaction = get_transaction_by_plaid_id(
        "modified_type_001"
    )

    assert transaction is not None
    assert transaction[10] == "refund"