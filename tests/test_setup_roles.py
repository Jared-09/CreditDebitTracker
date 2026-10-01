import pytest

from app.accounts import (
    add_account,
    get_account_by_role,
)

from app.setup_roles import (
    assign_account_role,
)


def test_assign_account_role_to_funding(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Savings",
        institution="Fairwinds",
        account_type="savings",
    )

    assign_account_role(
        account_id=account_id,
        account_role="funding",
    )

    account = get_account_by_role(
        "funding"
    )

    assert account is not None
    assert account[0] == account_id
    assert account[7] == "funding"


def test_assign_account_role_to_spending(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Checking",
        institution="Fairwinds",
        account_type="checking",
    )

    assign_account_role(
        account_id=account_id,
        account_role="spending",
    )

    account = get_account_by_role(
        "spending"
    )

    assert account is not None
    assert account[0] == account_id
    assert account[7] == "spending"


def test_assign_account_role_rejects_invalid_role(
    test_database,
):
    account_id = add_account(
        name="Test Account",
        institution="Test Bank",
        account_type="checking",
    )

    with pytest.raises(ValueError):
        assign_account_role(
            account_id=account_id,
            account_role="invalid_role",
        )


def test_assign_account_role_requires_existing_account(
    test_database,
):
    with pytest.raises(ValueError):
        assign_account_role(
            account_id=99999,
            account_role="funding",
        )