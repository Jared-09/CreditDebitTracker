from unittest.mock import Mock

from app.plaid import (
    create_sandbox_public_token,
    exchange_public_token,
)


def test_create_sandbox_public_token():
    client = Mock()

    response = Mock()
    response.public_token = "public-sandbox-test-token"

    client.sandbox_public_token_create.return_value = (
        response
    )

    public_token = create_sandbox_public_token(
        client=client,
    )

    assert public_token == "public-sandbox-test-token"

    client.sandbox_public_token_create.assert_called_once()


def test_exchange_public_token():
    client = Mock()

    response = Mock()
    response.access_token = "access-sandbox-test-token"
    response.item_id = "test-item-id"

    client.item_public_token_exchange.return_value = (
        response
    )

    result = exchange_public_token(
        client=client,
        public_token="public-sandbox-test-token",
    )

    assert result == {
        "access_token": "access-sandbox-test-token",
        "item_id": "test-item-id",
    }

    client.item_public_token_exchange.assert_called_once()