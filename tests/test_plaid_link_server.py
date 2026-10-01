from unittest.mock import patch

from app.plaid_link_server import app


def test_create_link_token_endpoint():

    client = app.test_client()

    with patch(
        "app.plaid_link_server.create_plaid_client"
    ) as mock_client, patch(
        "app.plaid_link_server.create_link_token",
        return_value="test-link-token",
    ):

        response = client.post(
            "/api/create_link_token"
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "link_token": "test-link-token"
    }

    mock_client.assert_called_once()


def test_exchange_public_token_endpoint():

    client = app.test_client()

    with patch(
        "app.plaid_link_server.create_plaid_client"
    ) as mock_client, patch(
        "app.plaid_link_server.exchange_public_token",
        return_value={
            "access_token": "test-access-token",
            "item_id": "test-item-id",
        },
    ), patch(
        "app.plaid_link_server.save_plaid_item"
    ) as mock_save:

        response = client.post(
            "/api/exchange_public_token",
            json={
                "public_token":
                    "test-public-token"
            },
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "success": True,
        "item_id": "test-item-id",
    }

    mock_client.assert_called_once()

    mock_save.assert_called_once_with(
        item_id="test-item-id",
        access_token="test-access-token",
    )