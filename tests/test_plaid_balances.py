from unittest.mock import Mock

from app.plaid import (
    get_plaid_account_balances,
)


def test_get_plaid_account_balances():

    client = Mock()

    balance = Mock()
    balance.current = 1250.75
    balance.available = 1100.25

    account = Mock()
    account.account_id = "plaid-account-123"
    account.name = "Fairwinds Savings"
    account.official_name = "Fairwinds Savings Account"
    account.type = "depository"
    account.subtype = "savings"
    account.balances = balance

    response = Mock()
    response.accounts = [
        account,
    ]

    client.accounts_balance_get.return_value = (
        response
    )

    result = get_plaid_account_balances(
        client=client,
        access_token="test-access-token",
    )

    assert len(result) == 1

    assert result[0]["plaid_account_id"] == (
        "plaid-account-123"
    )

    assert result[0]["name"] == (
        "Fairwinds Savings"
    )

    assert result[0]["current_balance"] == (
        1250.75
    )

    assert result[0]["available_balance"] == (
        1100.25
    )

    client.accounts_balance_get.assert_called_once()