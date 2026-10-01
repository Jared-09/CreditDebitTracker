from app.accounts import (
    add_account,
    get_account_by_plaid_account_id,
    set_account_balance,
    update_account_institution,
)
from app.plaid_items import (
    link_plaid_account_to_local_account,
)


def determine_account_type(
    plaid_account,
):
    """
    Convert Plaid account information into the
    application's account_type value.
    """

    account_type = plaid_account[
        "account_type"
    ]

    account_subtype = plaid_account[
        "account_subtype"
    ]

    if (
        account_type == "credit"
        and account_subtype == "credit card"
    ):
        return "credit_card"

    if account_type == "depository":
        if account_subtype == "savings":
            return "savings"

        return "checking"

    return account_type


def register_plaid_accounts(
    item_id,
    plaid_accounts,
    institution_name="Unknown Institution",
):
    """
    Register or update all accounts belonging to a
    Plaid Item.

    Returns the local account IDs associated with
    the Item.
    """

    local_account_ids = []

    for plaid_account in plaid_accounts:
        plaid_account_id = plaid_account[
            "plaid_account_id"
        ]

        existing_account_id = (
            get_account_by_plaid_account_id(
                plaid_account_id
            )
        )

        account_type = determine_account_type(
            plaid_account
        )

        current_balance = plaid_account[
            "current_balance"
        ]

        if existing_account_id is None:
            account_id = add_account(
                name=plaid_account["name"],
                institution=institution_name,
                account_type=account_type,
                last_four=plaid_account.get(
                    "mask"
                ),
                current_balance=current_balance,
                account_role=(
                    "credit_card"
                    if account_type == "credit_card"
                    else "other"
                ),
                plaid_account_id=plaid_account_id,
            )

        else:
            account_id = existing_account_id

            update_account_institution(
                account_id=account_id,
                institution=institution_name,
            )

            if current_balance is not None:
                set_account_balance(
                    account_id=account_id,
                    current_balance=current_balance,
                )

        link_plaid_account_to_local_account(
            plaid_account_id=plaid_account_id,
            account_id=account_id,
            item_id=item_id,
        )

        local_account_ids.append(
            account_id
        )

    return local_account_ids