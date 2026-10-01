from app.accounts import add_account
from app.plaid_pipeline import sync_plaid_transactions


def test_sync_plaid_transactions_into_database(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
        account_role="credit_card",
    )

    result = sync_plaid_transactions(
        account_id=account_id,
        added=[
            {
                "transaction_id": "txn_001",
                "merchant_name": "Coffee Shop",
                "name": "Coffee Shop",
                "date": "2026-09-30",
                "amount": 5.00,
                "pending": False,
            }
        ],
        modified=[],
        removed=[],
    )

    assert result["added"] == 1