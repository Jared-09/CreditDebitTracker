import pytest

from app.accounts import (
    add_account,
    get_account_by_role,
    set_account_role,
)


def test_set_account_role(
    test_database,
):
    account_id = add_account(
        name="Fairwinds Savings",
        institution="Fairwinds",
        account_type="savings",
    )

    set_account_role(
        account_id=account_id,
        account_role="funding",
    )

    account = get_account_by_role(
        "funding"
    )

    assert account is not None
    assert account[0] == account_id
    assert account[7] == "funding"


def test_unique_funding_role(
    test_database,
):
    first_id = add_account(
        name="Savings One",
        institution="Test Bank",
        account_type="savings",
        account_role="funding",
    )

    second_id = add_account(
        name="Savings Two",
        institution="Test Bank",
        account_type="savings",
    )

    with pytest.raises(ValueError):
        set_account_role(
            account_id=second_id,
            account_role="funding",
        )

    assert (
        get_account_by_role("funding")[0]
        == first_id
    )


def test_unique_spending_role(
    test_database,
):
    first_id = add_account(
        name="Checking One",
        institution="Test Bank",
        account_type="checking",
        account_role="spending",
    )

    second_id = add_account(
        name="Checking Two",
        institution="Test Bank",
        account_type="checking",
    )

    with pytest.raises(ValueError):
        set_account_role(
            account_id=second_id,
            account_role="spending",
        )

    assert (
        get_account_by_role("spending")[0]
        == first_id
    )


def test_account_can_change_from_other_to_credit_card(
    test_database,
):
    account_id = add_account(
        name="Chase Freedom",
        institution="Chase",
        account_type="credit_card",
    )

    set_account_role(
        account_id=account_id,
        account_role="credit_card",
    )

    account = get_account_by_role(
        "credit_card"
    )

    assert account is not None
    assert account[0] == account_id
    assert account[7] == "credit_card"