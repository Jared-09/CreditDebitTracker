from app.accounts import add_account
from app.sync import process_plaid_transaction
from app.transactions import get_transaction_by_plaid_id


def test_posted_reconciliation_updates_transaction_type(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    pending_database_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="pending_type_001",
        merchant_name="Pending Merchant",
        description="Pending transaction",
        transaction_date="2026-09-29",
        plaid_amount=50.00,
        pending=True,
        transaction_type="purchase",
    )

    posted_database_id = process_plaid_transaction(
        account_id=account_id,
        plaid_transaction_id="posted_type_001",
        pending_transaction_id="pending_type_001",
        merchant_name="Final Merchant",
        description="Final refund",
        transaction_date="2026-09-30",
        plaid_amount=50.00,
        pending=False,
        transaction_type="refund",
    )

    # Reconciliation must reuse the original database row.
    assert posted_database_id == pending_database_id

    transaction = get_transaction_by_plaid_id(
        "posted_type_001"
    )

    assert transaction is not None

    # The final posted classification must replace
    # the preliminary pending classification.
    assert transaction[10] == "refund"