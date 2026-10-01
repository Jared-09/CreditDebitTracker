from app.accounts import (
    add_account,
    get_account_by_plaid_account_id,
)


def test_get_account_by_plaid_account_id(
    test_database,
):
    account_id = add_account(
        name="Sandbox Credit Card",
        institution="Plaid Sandbox",
        account_type="credit_card",
        account_role="credit_card",
        plaid_account_id="plaid-card-123",
    )

    result = get_account_by_plaid_account_id(
        "plaid-card-123"
    )

    assert result == account_id


def test_get_account_by_plaid_account_id_returns_none(
    test_database,
):
    result = get_account_by_plaid_account_id(
        "does-not-exist"
    )

    assert result is None