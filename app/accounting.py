from decimal import Decimal, ROUND_HALF_UP

from app.accounts import get_account_balance
from app.transactions import get_credit_card_transactions


def to_money(value):
    """Convert a value to an exact two-decimal money value."""

    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def get_effective_amount(
    plaid_amount,
    manual_amount,
    pending,
):
    """Return the amount that should currently count toward spending."""

    if pending and manual_amount is not None:
        amount = to_money(manual_amount)
    else:
        amount = to_money(plaid_amount)

    return float(amount)


def calculate_total_spending(transactions):
    """Calculate total effective spending from transaction rows."""

    total = Decimal("0.00")

    for transaction in transactions:
        plaid_amount = transaction[7]
        manual_amount = transaction[8]
        pending = bool(transaction[9])
        transaction_type = transaction[10]

        if transaction_type != "purchase":
            continue

        effective_amount = get_effective_amount(
            plaid_amount=plaid_amount,
            manual_amount=manual_amount,
            pending=pending,
        )

        total += to_money(effective_amount)

    return float(to_money(total))


def calculate_remaining_liability(transactions):
    """Calculate remaining credit-card liability from transactions."""

    liability = Decimal("0.00")

    for transaction in transactions:
        plaid_amount = transaction[7]
        manual_amount = transaction[8]
        pending = bool(transaction[9])
        transaction_type = transaction[10]

        effective_amount = get_effective_amount(
            plaid_amount=plaid_amount,
            manual_amount=manual_amount,
            pending=pending,
        )

        effective_money = to_money(effective_amount)

        if transaction_type == "purchase":
            liability += effective_money

        elif transaction_type in ("payment", "refund"):
            liability -= effective_money

    if liability < Decimal("0.00"):
        liability = Decimal("0.00")

    return float(to_money(liability))


def calculate_transfer_needed(
    remaining_liability,
    ap_balance,
):
    """Calculate how much money still needs to be moved into AP."""

    liability = to_money(remaining_liability)
    funded = to_money(ap_balance)

    if funded < Decimal("0.00"):
        funded = Decimal("0.00")

    transfer_needed = liability - funded

    if transfer_needed < Decimal("0.00"):
        transfer_needed = Decimal("0.00")

    return float(to_money(transfer_needed))


def build_credit_card_control_summary(
    transactions,
    ap_balance,
):
    """Build the core Credit Card Control funding summary."""

    remaining_liability = calculate_remaining_liability(
        transactions
    )

    transfer_needed = calculate_transfer_needed(
        remaining_liability=remaining_liability,
        ap_balance=ap_balance,
    )

    liability_money = to_money(remaining_liability)
    ap_money = to_money(ap_balance)

    if ap_money < Decimal("0.00"):
        ap_money = Decimal("0.00")

    currently_funded = min(
        liability_money,
        ap_money,
    )

    return {
        "remaining_liability": float(
            to_money(liability_money)
        ),
        "currently_funded": float(
            to_money(currently_funded)
        ),
        "still_needs_funding": transfer_needed,
        "transfer_to_ap": transfer_needed,
    }


def build_credit_card_control_summary_from_database(
    ap_account_id,
    spending_account_id=None,
):
    """Build the control summary using stored database values."""

    transactions = get_credit_card_transactions()

    ap_balance = get_account_balance(
        ap_account_id
    )

    if ap_balance is None:
        raise ValueError(
            "The AP account does not have a current balance."
        )

    summary = build_credit_card_control_summary(
        transactions=transactions,
        ap_balance=ap_balance,
    )

    if spending_account_id is not None:
        available_to_spend = get_account_balance(
            spending_account_id
        )

        if available_to_spend is None:
            raise ValueError(
                "The spending account does not have a current balance."
            )

        summary["available_to_spend"] = float(
            to_money(available_to_spend)
        )

    return summary