from app.accounts import add_account
from app.plaid_items import (
    link_plaid_item_to_account,
    get_account_plaid_item,
)


def test_link_plaid_item_to_account(
    test_database,
):
    account_id = add_account(
        name="Test Credit Card",
        institution="Test Bank",
        account_type="credit_card",
        last_four="1234",
        account_role="credit_card",
    )

    link_plaid_item_to_account(
        item_id="test-item-id",
        account_id=account_id,
    )

    linked_account = get_account_plaid_item(
        "test-item-id"
    )

    assert linked_account == account_id