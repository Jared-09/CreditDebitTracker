from app.accounting import (
    build_credit_card_control_summary_from_database,
)
from app.accounts import add_account
from app.transactions import add_transaction


def test_control_summary_uses_stored_ap_balance(test_database):
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

    # Remaining credit-card liability = $760.19.
    add_transaction(
        account_id=credit_card_id,
        merchant_name="Purchase One",
        description="First purchase",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="database_summary_001",
    )

    add_transaction(
        account_id=credit_card_id,
        merchant_name="Purchase Two",
        description="Second purchase",
        transaction_date="2026-09-30",
        plaid_amount=260.19,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="database_summary_002",
    )

    summary = build_credit_card_control_summary_from_database(
        ap_account_id=fairwinds_ap_id,
    )

    assert summary["remaining_liability"] == 760.19
    assert summary["currently_funded"] == 612.37
    assert summary["still_needs_funding"] == 147.82
    assert summary["transfer_to_ap"] == 147.82


def test_control_summary_ignores_non_credit_card_transactions(
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
        current_balance=100.00,
    )

    fairwinds_checking_id = add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="9012",
        current_balance=750.00,
    )

    # This is real credit-card liability.
    add_transaction(
        account_id=credit_card_id,
        merchant_name="Card Purchase",
        description="Credit card purchase",
        transaction_date="2026-09-30",
        plaid_amount=250.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="summary_filter_card_001",
    )

    # This transaction belongs to checking and must not count
    # toward credit-card liability.
    add_transaction(
        account_id=fairwinds_checking_id,
        merchant_name="Checking Activity",
        description="Non-card transaction",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="summary_filter_checking_001",
    )

    summary = build_credit_card_control_summary_from_database(
        ap_account_id=fairwinds_ap_id,
        spending_account_id=fairwinds_checking_id,
    )

    assert summary["available_to_spend"] == 750.00

    # Only the $250 credit-card purchase counts.
    assert summary["remaining_liability"] == 250.00

    # $100 is already sitting in AP.
    assert summary["currently_funded"] == 100.00

    # Therefore only $150 still needs to move to AP.
    assert summary["still_needs_funding"] == 150.00
    assert summary["transfer_to_ap"] == 150.00