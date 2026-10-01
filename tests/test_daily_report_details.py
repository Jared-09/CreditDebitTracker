from unittest.mock import patch

from app.reporting import build_daily_report


def test_daily_report_contains_funding_details():

    with patch(
        "app.reporting.build_credit_card_control_summary_from_roles"
    ) as mock_summary:

        mock_summary.return_value = {
            "total_liability": 1000,
            "funded_amount": 700,
            "transfer_to_ap": 300,
            "available_to_spend": 750,
        }

        report = build_daily_report()

        assert report["total_liability"] == 1000
        assert report["funded_amount"] == 700
        assert report["transfer_needed"] == 300
        assert report["available_to_spend"] == 750