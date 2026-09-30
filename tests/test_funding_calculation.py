from app.accounting import calculate_transfer_needed


def test_transfer_needed_with_no_existing_funding():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=500.00,
        ap_balance=0.00,
    )

    assert transfer_needed == 500.00


def test_transfer_needed_with_partial_existing_funding():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=650.00,
        ap_balance=500.00,
    )

    assert transfer_needed == 150.00


def test_card_payment_does_not_create_new_funding_need():
    # Before the payment:
    # $650 liability - $500 AP = $150 still needed.
    before_payment = calculate_transfer_needed(
        remaining_liability=650.00,
        ap_balance=500.00,
    )

    # A $300 card payment is made from AP.
    #
    # Liability: $650 -> $350
    # AP balance: $500 -> $200
    #
    # The funding shortage should still be exactly $150.
    after_payment = calculate_transfer_needed(
        remaining_liability=350.00,
        ap_balance=200.00,
    )

    assert before_payment == 150.00
    assert after_payment == 150.00


def test_transfer_needed_never_goes_negative():
    transfer_needed = calculate_transfer_needed(
        remaining_liability=200.00,
        ap_balance=300.00,
    )

    assert transfer_needed == 0.00