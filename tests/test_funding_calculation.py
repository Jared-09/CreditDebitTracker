from app.accounting import (
    build_credit_card_control_summary,
    calculate_transfer_needed,
)


def test_no_transfer_needed_when_fully_funded():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=500.00,
        ap_balance=500.00,
    )

    assert transfer_needed == 0.00


def test_transfer_needed_when_partially_funded():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=500.00,
        ap_balance=350.00,
    )

    assert transfer_needed == 150.00


def test_no_transfer_needed_when_overfunded():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=500.00,
        ap_balance=600.00,
    )

    assert transfer_needed == 0.00


def test_zero_liability_needs_no_transfer():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=0.00,
        ap_balance=100.00,
    )

    assert transfer_needed == 0.00


def test_negative_ap_balance_counts_as_zero_funded():
    summary = build_credit_card_control_summary(
        transactions=[],
        ap_balance=-25.00,
    )

    assert summary["remaining_liability"] == 0.00
    assert summary["currently_funded"] == 0.00
    assert summary["still_needs_funding"] == 0.00
    assert summary["transfer_to_ap"] == 0.00


def test_negative_ap_balance_does_not_reduce_transfer_needed():
    transactions = [
        (
            1,
            1,
            "negative_ap_purchase_001",
            None,
            "Test Merchant",
            "Test purchase",
            "2026-09-30",
            500.00,
            None,
            0,
            "purchase",
        )
    ]

    summary = build_credit_card_control_summary(
        transactions=transactions,
        ap_balance=-25.00,
    )

    assert summary["remaining_liability"] == 500.00
    assert summary["currently_funded"] == 0.00
    assert summary["still_needs_funding"] == 500.00
    assert summary["transfer_to_ap"] == 500.00