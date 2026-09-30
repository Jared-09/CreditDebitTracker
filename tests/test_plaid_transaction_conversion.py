from app.plaid import convert_plaid_transaction


def test_convert_plaid_purchase():
    plaid_transaction = {
        "transaction_id": "plaid_purchase_001",
        "pending_transaction_id": None,
        "merchant_name": "Target",
        "name": "Target Purchase",
        "date": "2026-09-30",
        "amount": 47.36,
        "pending": True,
        "personal_finance_category": {
            "primary": "GENERAL_MERCHANDISE",
        },
    }

    converted = convert_plaid_transaction(
        plaid_transaction
    )

    assert converted == {
        "plaid_transaction_id": "plaid_purchase_001",
        "pending_transaction_id": None,
        "merchant_name": "Target",
        "description": "Target Purchase",
        "transaction_date": "2026-09-30",
        "plaid_amount": 47.36,
        "pending": True,
        "transaction_type": "purchase",
    }


def test_convert_plaid_payment():
    plaid_transaction = {
        "transaction_id": "plaid_payment_001",
        "pending_transaction_id": None,
        "merchant_name": None,
        "name": "Credit Card Payment",
        "date": "2026-09-30",
        "amount": -500.00,
        "pending": False,
        "personal_finance_category": {
            "primary": "LOAN_PAYMENTS",
        },
    }

    converted = convert_plaid_transaction(
        plaid_transaction
    )

    assert converted["plaid_amount"] == 500.00
    assert converted["transaction_type"] == "payment"
    assert converted["pending"] is False


def test_convert_plaid_refund():
    plaid_transaction = {
        "transaction_id": "plaid_refund_001",
        "pending_transaction_id": "original_pending_001",
        "merchant_name": "Target",
        "name": "Target Refund",
        "date": "2026-09-30",
        "amount": -25.00,
        "pending": False,
        "personal_finance_category": {
            "primary": "GENERAL_MERCHANDISE",
        },
    }

    converted = convert_plaid_transaction(
        plaid_transaction
    )

    assert converted["plaid_amount"] == 25.00
    assert converted["transaction_type"] == "refund"
    assert (
        converted["pending_transaction_id"]
        == "original_pending_001"
    )


def test_convert_plaid_transaction_without_category():
    plaid_transaction = {
        "transaction_id": "plaid_purchase_002",
        "pending_transaction_id": None,
        "merchant_name": "Local Store",
        "name": "Local Store",
        "date": "2026-09-30",
        "amount": 12.50,
        "pending": False,
        "personal_finance_category": None,
    }

    converted = convert_plaid_transaction(
        plaid_transaction
    )

    assert converted["plaid_amount"] == 12.50
    assert converted["transaction_type"] == "purchase"