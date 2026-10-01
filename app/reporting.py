from app.accounting import (
    build_credit_card_control_summary_from_database,
    build_credit_card_control_summary_from_roles,
)


def build_daily_report():
    """
    Build the daily credit card funding report.

    Supports both the current accounting summary field names
    and the legacy names used by existing callers/tests.
    """

    summary = (
        build_credit_card_control_summary_from_roles()
    )

    if "remaining_liability" in summary:
        total_liability = summary[
            "remaining_liability"
        ]
    else:
        total_liability = summary[
            "total_liability"
        ]

    if "currently_funded" in summary:
        funded_amount = summary[
            "currently_funded"
        ]
    else:
        funded_amount = summary[
            "funded_amount"
        ]

    return {
        "total_liability": total_liability,
        "funded_amount": funded_amount,
        "transfer_needed": summary[
            "transfer_to_ap"
        ],
        "available_to_spend": summary.get(
            "available_to_spend",
            None,
        ),
    }


def print_daily_report():

    report = build_daily_report()

    print()
    print("================================")
    print("Credit Card Control Report")
    print("================================")
    print()

    print(
        f"Total Card Liability: "
        f"${report['total_liability']:.2f}"
    )

    print(
        f"Already Funded: "
        f"${report['funded_amount']:.2f}"
    )

    print(
        f"Transfer Needed: "
        f"${report['transfer_needed']:.2f}"
    )

    if report["available_to_spend"] is not None:
        print(
            f"Available To Spend: "
            f"${report['available_to_spend']:.2f}"
        )

    print()
    print("================================")