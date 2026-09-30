from app.accounting import (
    build_credit_card_control_summary_from_roles,
)
from app.accounts import add_account
from app.transactions import add_transaction


def test_control_summary_finds_accounts_by_role(
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
        current_balance=612.37,
        account_role="funding",
    )

    add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="9012",
        current_balance=823.41,
        account_role="spending",
    )

    add_transaction(
        account_id=credit_card_id,
        merchant_name="Test Purchase",
        description="Credit card purchase",
        transaction_date="2026-09-30",
        plaid_amount=760.19,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="role_summary_001",
    )

    summary = build_credit_card_control_summary_from_roles()

    assert summary["available_to_spend"] == 823.41
    assert summary["remaining_liability"] == 760.19
    assert summary["currently_funded"] == 612.37
    assert summary["still_needs_funding"] == 147.82
    assert summary["transfer_to_ap"] == 147.82