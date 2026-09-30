from app.accounting import calculate_remaining_liability


def test_liability_accounts_for_purchases_payments_and_refunds():
    transactions = [
        (
            1,
            1,
            "purchase_001",
            None,
            "Merchant",
            "Purchase",
            "2026-09-30",
            500.00,
            None,
            0,
            "purchase",
        ),
        (
            2,
            1,
            "payment_001",
            None,
            "Payment",
            "Card payment",
            "2026-09-30",
            100.00,
            None,
            0,
            "payment",
        ),
        (
            3,
            1,
            "refund_001",
            None,
            "Merchant",
            "Refund",
            "2026-09-30",
            50.00,
            None,
            0,
            "refund",
        ),
    ]

    liability = calculate_remaining_liability(
        transactions
    )

    assert liability == 350.00


def test_pending_payment_does_not_reduce_liability():
    transactions = [
        (
            1,
            1,
            "purchase_002",
            None,
            "Merchant",
            "Purchase",
            "2026-09-30",
            500.00,
            None,
            0,
            "purchase",
        ),
        (
            2,
            1,
            "payment_002",
            None,
            "Payment",
            "Pending card payment",
            "2026-09-30",
            200.00,
            None,
            1,
            "payment",
        ),
    ]

    liability = calculate_remaining_liability(
        transactions
    )

    assert liability == 500.00


def test_pending_refund_does_not_reduce_liability():
    transactions = [
        (
            1,
            1,
            "purchase_003",
            None,
            "Merchant",
            "Purchase",
            "2026-09-30",
            500.00,
            None,
            0,
            "purchase",
        ),
        (
            2,
            1,
            "refund_002",
            None,
            "Merchant",
            "Pending refund",
            "2026-09-30",
            150.00,
            None,
            1,
            "refund",
        ),
    ]

    liability = calculate_remaining_liability(
        transactions
    )

    assert liability == 500.00