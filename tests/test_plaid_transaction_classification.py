from app.plaid import classify_plaid_transaction


def test_positive_credit_card_transaction_is_purchase():
    transaction_type = classify_plaid_transaction(
        plaid_amount=47.36,
        primary_category="GENERAL_MERCHANDISE",
    )

    assert transaction_type == "purchase"


def test_negative_credit_card_payment_is_payment():
    transaction_type = classify_plaid_transaction(
        plaid_amount=-500.00,
        primary_category="LOAN_PAYMENTS",
    )

    assert transaction_type == "payment"


def test_negative_non_payment_transaction_is_refund():
    transaction_type = classify_plaid_transaction(
        plaid_amount=-25.00,
        primary_category="GENERAL_MERCHANDISE",
    )

    assert transaction_type == "refund"


def test_positive_amount_is_purchase_even_with_missing_category():
    transaction_type = classify_plaid_transaction(
        plaid_amount=12.50,
        primary_category=None,
    )

    assert transaction_type == "purchase"