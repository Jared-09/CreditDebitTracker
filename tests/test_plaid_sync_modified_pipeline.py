from app.accounts import add_account
from app.plaid_pipeline import sync_plaid_transactions
from app.transactions import get_transaction_by_plaid_id


def test_sync_plaid_modified_transaction(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
        account_role="credit_card",
    )

    sync_plaid_transactions(
        account_id=account_id,
        added=[
            {
                "transaction_id": "txn_modified_001",
                "merchant_name": "Restaurant",
                "name": "Pending Restaurant",
                "date": "2026-09-29",
                "amount": 60.00,
                "pending": True,
            }
        ],
        modified=[],
        removed=[],
    )

    sync_plaid_transactions(
        account_id=account_id,
        added=[],
        modified=[
            {
                "transaction_id": "txn_modified_001",
                "merchant_name": "Restaurant",
                "name": "Final Restaurant",
                "date": "2026-09-30",
                "amount": 71.84,
                "pending": False,
            }
        ],
        removed=[],
    )

    transaction = get_transaction_by_plaid_id(
        "txn_modified_001"
    )

    assert transaction is not None
    assert transaction[7] == 71.84
    assert transaction[9] == 0