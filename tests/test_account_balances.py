import pytest

from app.accounts import (
    add_account,
    get_account_balance,
    set_account_balance,
)


def test_account_can_be_created_with_balance(test_database):
    account_id = add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="1234",
        current_balance=612.37,
    )

    balance = get_account_balance(account_id)

    assert balance == 612.37


def test_account_balance_can_be_updated(test_database):
    account_id = add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="5678",
        current_balance=750.00,
    )

    set_account_balance(
        account_id=account_id,
        current_balance=823.41,
    )

    balance = get_account_balance(account_id)

    assert balance == 823.41


def test_missing_account_balance_lookup_raises(test_database):
    with pytest.raises(ValueError):
        get_account_balance(999999)


def test_missing_account_balance_update_raises(test_database):
    with pytest.raises(ValueError):
        set_account_balance(
            account_id=999999,
            current_balance=100.00,
        )