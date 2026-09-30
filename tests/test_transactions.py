from app.accounting import get_effective_amount


def test_pending_transaction_without_manual_override():
    effective_amount = get_effective_amount(
        plaid_amount=1.00,
        manual_amount=None,
        pending=True,
    )

    assert effective_amount == 1.00


def test_pending_transaction_with_manual_override():
    effective_amount = get_effective_amount(
        plaid_amount=1.00,
        manual_amount=47.36,
        pending=True,
    )

    assert effective_amount == 47.36


def test_posted_transaction_uses_plaid_amount():
    effective_amount = get_effective_amount(
        plaid_amount=48.10,
        manual_amount=47.36,
        pending=False,
    )

    assert effective_amount == 48.10