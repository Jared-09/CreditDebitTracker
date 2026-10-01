from app.accounts import (
    get_all_accounts,
    set_account_role,
)


VALID_ROLES = {
    "credit_card",
    "funding",
    "spending",
    "other",
}


def print_accounts():
    """Display all accounts and their current roles."""

    accounts = get_all_accounts()

    print()
    print("================================")
    print("Account Roles")
    print("================================")
    print()

    if not accounts:
        print("No accounts are configured.")
        print()
        return

    for account in accounts:
        (
            account_id,
            name,
            institution,
            account_type,
            last_four,
            active,
            current_balance,
            account_role,
        ) = account

        balance = (
            f"${current_balance:.2f}"
            if current_balance is not None
            else "N/A"
        )

        print(
            f"ID {account_id}: "
            f"{name} "
            f"({institution})"
        )

        print(
            f"  Type: {account_type}"
        )

        print(
            f"  Balance: {balance}"
        )

        print(
            f"  Role: {account_role}"
        )

        if last_four:
            print(
                f"  Last Four: {last_four}"
            )

        print()


def assign_account_role(
    account_id,
    account_role,
):
    """Assign an application role to an account."""

    if account_role not in VALID_ROLES:
        raise ValueError(
            f"Invalid account role: {account_role}"
        )

    set_account_role(
        account_id=account_id,
        account_role=account_role,
    )


def main():
    """Interactively assign an account role."""

    print_accounts()

    account_id_text = input(
        "Enter account ID to configure: "
    ).strip()

    try:
        account_id = int(account_id_text)
    except ValueError:
        print("Account ID must be a number.")
        return

    print()
    print("Available roles:")
    print("  credit_card")
    print("  funding")
    print("  spending")
    print("  other")
    print()

    account_role = input(
        "Enter new role: "
    ).strip().lower()

    try:
        assign_account_role(
            account_id=account_id,
            account_role=account_role,
        )

    except ValueError as error:
        print()
        print(f"Error: {error}")
        return

    print()
    print("Account role updated successfully.")
    print()


if __name__ == "__main__":
    main()