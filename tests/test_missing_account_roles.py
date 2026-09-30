import pytest

from app.accounting import (
    build_credit_card_control_summary_from_roles,
)
from app.accounts import add_account


def test_missing_funding_account_is_rejected(
    test_database,
):
    add_account(
        name="Fairwinds Spend Smart Checking",
        institution="Fairwinds",
        account_type="checking",
        last_four="1234",
        current_balance=750.00,
        account_role="spending",
    )

    with pytest.raises(
        ValueError,
        match="No funding account is configured",
    ):
        build_credit_card_control_summary_from_roles()


def test_missing_spending_account_is_rejected(
    test_database,
):
    add_account(
        name="Fairwinds AP",
        institution="Fairwinds",
        account_type="savings",
        last_four="5678",
        current_balance=500.00,
        account_role="funding",
    )

    with pytest.raises(
        ValueError,
        match="No spending account is configured",
    ):
        build_credit_card_control_summary_from_roles()