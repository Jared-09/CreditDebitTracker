from unittest.mock import patch

from app.reporting import build_daily_report


def test_build_daily_report():

    with patch(
        "app.reporting.build_credit_card_control_summary_from_roles"
    ) as mock_summary:

        mock_summary.return_value = {
            "total_liability": 500,
            "funded_amount": 300,
            "transfer_to_ap": 200,
            "available_to_spend": 750,
        }

        report = build_daily_report()

        assert report["total_liability"] == 500
        assert report["funded_amount"] == 300
        assert report["transfer_needed"] == 200
        assert report["available_to_spend"] == 750