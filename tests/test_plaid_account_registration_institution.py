from app.accounts import (
    get_all_accounts,
)
from app.plaid_items import (
    save_plaid_item,
)
from app.plaid_account_registration import (
    register_plaid_accounts,
)


def test_registration_stores_institution_name(
    test_database,
):
    plaid_account_id = "plaid-institution-test"
    item_id = "item-institution-test"

    save_plaid_item(
        item_id=item_id,
        access_token="test-access-token",
    )

    register_plaid_accounts(
        item_id=item_id,
        plaid_accounts=[
            {
                "plaid_account_id": plaid_account_id,
                "name": "Spend Smart Checking",
                "official_name": "Spend Smart Checking",
                "mask": "1234",
                "account_type": "depository",
                "account_subtype": "checking",
                "current_balance": 384.76,
                "available_balance": 384.76,
            }
        ],
        institution_name="Fairwinds",
    )

    accounts = get_all_accounts()

    account = next(
        account
        for account in accounts
        if account[4] == "1234"
    )

    assert account[2] == "Fairwinds"
    assert account[6] == 384.76