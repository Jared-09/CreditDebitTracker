def get_effective_amount(
    plaid_amount,
    manual_amount,
    pending,
):
    """Return the amount that should currently count toward spending."""

    if pending and manual_amount is not None:
        return manual_amount

    return plaid_amount


def calculate_total_spending(transactions):
    """Calculate total effective spending from transaction rows."""

    total = 0.0

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

        total += effective_amount

    return round(total, 2)


def calculate_transfer_needed(
    remaining_liability,
    ap_balance,
):
    """Calculate how much money still needs to be moved into AP."""

    transfer_needed = remaining_liability - ap_balance

    if transfer_needed < 0:
        transfer_needed = 0.0

    return round(transfer_needed, 2)