from app.accounts import (
    add_account,
    get_account_balance,
    update_account_balance_by_plaid_id,
)


def test_update_account_balance_by_plaid_id(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Savings",
        institution="Fairwinds",
        account_type="savings",
        current_balance=100.00,
        account_role="funding",
        plaid_account_id="plaid-account-123",
    )

    update_account_balance_by_plaid_id(
        plaid_account_id="plaid-account-123",
        current_balance=1250.75,
    )

    assert get_account_balance(
        account_id
    ) == 1250.75