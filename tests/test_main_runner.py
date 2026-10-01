from unittest.mock import patch


def test_main_runs():

    with patch(
        "main.initialize_database"
    ) as mock_initialize, patch(
        "main.create_plaid_client"
    ) as mock_client, patch(
        "main.sync_all_plaid_accounts"
    ) as mock_sync, patch(
        "main.print_daily_report"
    ) as mock_report:

        mock_client.return_value = "client"

        mock_sync.return_value = [
            {
                "account_id": 1
            }
        ]

        from main import main

        main()

        mock_initialize.assert_called_once()

        mock_client.assert_called_once()

        mock_sync.assert_called_once()

        mock_report.assert_called_once()