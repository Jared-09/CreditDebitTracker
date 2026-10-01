from unittest.mock import patch

from app.accounts import add_account
from app.plaid_pipeline import sync_plaid_transactions


def test_transactions_use_their_plaid_account_id(
    test_database,
):
    checking_id = add_account(
        name="Sandbox Checking",
        institution="Plaid Sandbox",
        account_type="checking",
        account_role="spending",
        plaid_account_id="plaid-checking-123",
    )

    credit_card_id = add_account(
        name="Sandbox Credit Card",
        institution="Plaid Sandbox",
        account_type="credit_card",
        account_role="credit_card",
        plaid_account_id="plaid-card-456",
    )

    added = [
        {
            "account_id": "plaid-checking-123",
            "transaction_id": "transaction-checking",
            "amount": 25.00,
            "pending": False,
            "date": "2026-09-30",
            "merchant_name": "Checking Merchant",
            "name": "Checking Purchase",
        },
        {
            "account_id": "plaid-card-456",
            "transaction_id": "transaction-card",
            "amount": 75.00,
            "pending": False,
            "date": "2026-09-30",
            "merchant_name": "Card Merchant",
            "name": "Card Purchase",
        },
    ]

    with patch(
        "app.plaid_pipeline.process_plaid_transaction"
    ) as mock_process:

        result = sync_plaid_transactions(
            account_id=checking_id,
            added=added,
            modified=[],
            removed=[],
        )

    assert result["added"] == 2

    assert mock_process.call_count == 2

    first_call = mock_process.call_args_list[0]
    second_call = mock_process.call_args_list[1]

    assert first_call.kwargs["account_id"] == checking_id
    assert second_call.kwargs["account_id"] == credit_card_id