from app.database import get_connection

from app.plaid_account_registration import (
    determine_account_type,
    register_plaid_accounts,
)


def test_determine_credit_card_type():
    account = {
        "account_type": "credit",
        "account_subtype": "credit card",
    }

    assert (
        determine_account_type(account)
        == "credit_card"
    )


def test_determine_savings_type():
    account = {
        "account_type": "depository",
        "account_subtype": "savings",
    }

    assert (
        determine_account_type(account)
        == "savings"
    )


def test_determine_checking_type():
    account = {
        "account_type": "depository",
        "account_subtype": "checking",
    }

    assert (
        determine_account_type(account)
        == "checking"
    )


def test_register_plaid_accounts(
    test_database,
):
    from app.plaid_items import (
        save_plaid_item,
    )

    save_plaid_item(
        item_id="item-registration-1",
        access_token="access-token",
    )

    accounts = [
        {
            "plaid_account_id": "plaid-credit-1",
            "name": "Test Credit Card",
            "official_name": "Test Credit Card",
            "mask": "1234",
            "account_type": "credit",
            "account_subtype": "credit card",
            "current_balance": 125.50,
            "available_balance": 874.50,
        },
        {
            "plaid_account_id": "plaid-checking-1",
            "name": "Test Checking",
            "official_name": "Test Checking",
            "mask": "5678",
            "account_type": "depository",
            "account_subtype": "checking",
            "current_balance": 500.00,
            "available_balance": 450.00,
        },
    ]

    account_ids = register_plaid_accounts(
        item_id="item-registration-1",
        plaid_accounts=accounts,
    )

    assert len(account_ids) == 2

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                account_type,
                account_role,
                current_balance,
                plaid_account_id
            FROM accounts
            WHERE id IN (?, ?)
            ORDER BY id
            """,
            tuple(account_ids),
        ).fetchall()

    finally:
        connection.close()

    assert len(rows) == 2

    credit_card = next(
        row
        for row in rows
        if row[2] == "credit_card"
    )

    checking = next(
        row
        for row in rows
        if row[2] == "checking"
    )

    assert credit_card[3] == "credit_card"
    assert credit_card[4] == 125.50
    assert (
        credit_card[5]
        == "plaid-credit-1"
    )

    assert checking[3] == "other"
    assert checking[4] == 500.00
    assert (
        checking[5]
        == "plaid-checking-1"
    )