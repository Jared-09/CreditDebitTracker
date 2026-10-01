from app.accounts import (
    add_account,
)

from app.plaid_items import (
    link_plaid_account_to_local_account,
    save_plaid_item,
)


def test_link_plaid_account_to_local_account(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Savings",
        institution="Fairwinds",
        account_type="savings",
        account_role="funding",
    )

    link_plaid_account_to_local_account(
        plaid_account_id="plaid-savings-123",
        account_id=account_id,
    )

    from app.database import get_connection

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT plaid_account_id
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()

    finally:
        connection.close()

    assert row[0] == "plaid-savings-123"


def test_link_plaid_account_to_local_account_with_item(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Savings",
        institution="Fairwinds",
        account_type="savings",
        account_role="funding",
    )

    save_plaid_item(
        item_id="item-123",
        access_token="access-token-123",
    )

    link_plaid_account_to_local_account(
        plaid_account_id="plaid-savings-123",
        account_id=account_id,
        item_id="item-123",
    )

    from app.database import get_connection

    connection = get_connection()

    try:
        account_row = connection.execute(
            """
            SELECT plaid_account_id
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()

        link_row = connection.execute(
            """
            SELECT item_id, account_id
            FROM plaid_item_accounts
            WHERE item_id = ?
              AND account_id = ?
            """,
            (
                "item-123",
                account_id,
            ),
        ).fetchone()

    finally:
        connection.close()

    assert account_row[0] == "plaid-savings-123"

    assert link_row == (
        "item-123",
        account_id,
    )