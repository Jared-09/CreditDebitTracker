from app.plaid import normalize_plaid_amount


def test_positive_plaid_amount_remains_positive():
    amount = normalize_plaid_amount(47.36)

    assert amount == 47.36


def test_negative_plaid_amount_becomes_positive_magnitude():
    amount = normalize_plaid_amount(-500.00)

    assert amount == 500.00


def test_zero_plaid_amount_remains_zero():
    amount = normalize_plaid_amount(0.00)

    assert amount == 0.00