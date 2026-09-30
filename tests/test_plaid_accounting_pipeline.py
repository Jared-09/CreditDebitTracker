from app.accounting import (
    build_credit_card_control_summary_from_roles,
)
from app.accounts import add_account
from app.plaid import convert_plaid_transaction
from app.sync import process_plaid_sync_batch


def test_plaid_purchase_flows_into_funding_summary(
    test_database,
):
    credit_card_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
        account_role="credit_card",
    )

    add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="5678",
        current_balance=100.00,
        account_role="funding",
    )

    add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="9012",
        current_balance=650.00,
        account_role="spending",
    )

    raw_plaid_transaction = {
        "transaction_id": "plaid_purchase_001",
        "pending_transaction_id": None,
        "merchant_name": "Target",
        "name": "Target Purchase",
        "date": "2026-09-30",
        "amount": 147.36,
        "pending": False,
        "personal_finance_category": {
            "primary": "GENERAL_MERCHANDISE",
        },
    }

    converted_transaction = convert_plaid_transaction(
        raw_plaid_transaction
    )

    process_plaid_sync_batch(
        account_id=credit_card_id,
        added=[converted_transaction],
    )

    summary = (
        build_credit_card_control_summary_from_roles()
    )

    assert summary["remaining_liability"] == 147.36
    assert summary["currently_funded"] == 100.00
    assert summary["still_needs_funding"] == 47.36
    assert summary["transfer_to_ap"] == 47.36
    assert summary["available_to_spend"] == 650.00