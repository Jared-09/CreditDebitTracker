def get_effective_amount(plaid_amount, manual_amount, pending):
    """Return the amount that should currently count toward spending."""

    if pending and manual_amount is not None:
        return manual_amount

    return plaid_amount