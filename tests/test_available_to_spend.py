from app.accounting import (
    build_credit_card_control_summary_from_database,
)
from app.accounts import (
    add_account,
    set_account_balance,
)
from app.transactions import add_transaction


def test_spending_balance_does_not_change_ap_funding_need(
    test_database,
):
    credit_card_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    fairwinds_ap_id = add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="5678",
        current_balance=612.37,
    )

    fairwinds_checking_id = add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="9012",
        current_balance=823.41,
    )

    # Remaining card liability = $760.19.
    add_transaction(
        account_id=credit_card_id,
        merchant_name="Purchase",
        description="Credit card purchase",
        transaction_date="2026-09-30",
        plaid_amount=760.19,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="available_spend_001",
    )

    first_summary = (
        build_credit_card_control_summary_from_database(
            ap_account_id=fairwinds_ap_id,
            spending_account_id=fairwinds_checking_id,
        )
    )

    assert first_summary["available_to_spend"] == 823.41
    assert first_summary["currently_funded"] == 612.37
    assert first_summary["transfer_to_ap"] == 147.82

    # Change only the spending-account balance.
    set_account_balance(
        account_id=fairwinds_checking_id,
        current_balance=400.00,
    )

    second_summary = (
        build_credit_card_control_summary_from_database(
            ap_account_id=fairwinds_ap_id,
            spending_account_id=fairwinds_checking_id,
        )
    )

    assert second_summary["available_to_spend"] == 400.00

    # AP funding must remain completely unchanged.
    assert second_summary["currently_funded"] == 612.37
    assert second_summary["still_needs_funding"] == 147.82
    assert second_summary["transfer_to_ap"] == 147.82