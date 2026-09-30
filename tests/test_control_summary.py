from app.accounting import build_credit_card_control_summary
from app.accounts import add_account
from app.transactions import (
    add_transaction,
    get_all_transactions,
)


def test_credit_card_control_summary(test_database):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    # Total remaining card liability = $760.19.
    add_transaction(
        account_id=account_id,
        merchant_name="Purchase One",
        description="First purchase",
        transaction_date="2026-09-30",
        plaid_amount=500.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="summary_purchase_001",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Purchase Two",
        description="Second purchase",
        transaction_date="2026-09-30",
        plaid_amount=260.19,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="summary_purchase_002",
    )

    transactions = get_all_transactions()

    summary = build_credit_card_control_summary(
        transactions=transactions,
        ap_balance=612.37,
    )

    assert summary["remaining_liability"] == 760.19
    assert summary["currently_funded"] == 612.37
    assert summary["still_needs_funding"] == 147.82
    assert summary["transfer_to_ap"] == 147.82


def test_summary_caps_currently_funded_at_liability(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
    )

    add_transaction(
        account_id=account_id,
        merchant_name="Purchase",
        description="Purchase",
        transaction_date="2026-09-30",
        plaid_amount=200.00,
        pending=False,
        transaction_type="purchase",
        plaid_transaction_id="summary_overfunded_001",
    )

    transactions = get_all_transactions()

    summary = build_credit_card_control_summary(
        transactions=transactions,
        ap_balance=300.00,
    )

    assert summary["remaining_liability"] == 200.00
    assert summary["currently_funded"] == 200.00
    assert summary["still_needs_funding"] == 0.00
    assert summary["transfer_to_ap"] == 0.00