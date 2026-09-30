import pytest

from app.accounts import (
    add_account,
    get_account_by_role,
)


def test_account_can_be_retrieved_by_role(
    test_database,
):
    fairwinds_ap_id = add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="1234",
        account_role="funding",
    )

    account = get_account_by_role("funding")

    assert account is not None
    assert account[0] == fairwinds_ap_id
    assert account[1] == "Fairwinds AP"
    assert account[2] == "Fairwinds"
    assert account[3] == "savings"
    assert account[7] == "funding"


def test_duplicate_special_account_role_is_rejected(
    test_database,
):
    add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="1234",
        account_role="funding",
    )

    with pytest.raises(
        ValueError,
        match="Account role funding is already assigned",
    ):
        add_account(
            name="Wrong Funding Account",
            institution="Other Bank",
            account_type="savings",
            last_four="5678",
            account_role="funding",
        )


def test_invalid_account_role_is_rejected(
    test_database,
):
    with pytest.raises(
        ValueError,
        match="Invalid account role",
    ):
        add_account(
            name="Test Account",
            institution="Test Bank",
            account_type="checking",
            last_four="1234",
            account_role="banana",
        )