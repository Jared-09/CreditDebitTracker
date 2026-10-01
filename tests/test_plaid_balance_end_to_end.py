from app.accounts import (
    add_account,
    get_account_balance,
)
from app.plaid_items import (
    link_plaid_account_to_local_account,
)
from app.accounts import (
    update_account_balance_by_plaid_id,
)


def test_plaid_balance_updates_local_account(
    test_database,
):
    account_id = add_account(
        name="Sandbox Savings",
        institution="Plaid Sandbox",
        account_type="savings",
        account_role="funding",
        plaid_account_id="sandbox-saving-123",
    )

    link_plaid_account_to_local_account(
        plaid_account_id="sandbox-saving-123",
        account_id=account_id,
    )

    update_account_balance_by_plaid_id(
        plaid_account_id="sandbox-saving-123",
        current_balance=210.00,
    )

    assert get_account_balance(
        account_id
    ) == 210.00