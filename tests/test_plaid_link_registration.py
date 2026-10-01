from app.plaid_link_server import (
    app,
)


def test_exchange_public_token_registers_accounts(
    monkeypatch,
    test_database,
):

    captured = {}

    monkeypatch.setattr(
        "app.plaid_link_server.create_plaid_client",
        lambda: "test-client",
    )

    monkeypatch.setattr(
        "app.plaid_link_server.exchange_public_token",
        lambda client, public_token: {
            "item_id": "item-link-test",
            "access_token": "access-link-test",
        },
    )

    monkeypatch.setattr(
        "app.plaid_link_server.save_plaid_item",
        lambda item_id, access_token: (
            captured.update(
                {
                    "item_id": item_id,
                    "access_token": access_token,
                }
            )
        ),
    )

    monkeypatch.setattr(
        "app.plaid_link_server.get_plaid_account_balances",
        lambda client, access_token: [
            {
                "plaid_account_id": "plaid-link-account-1",
                "name": "Test Checking",
                "official_name": "Test Checking",
                "mask": "1234",
                "account_type": "depository",
                "account_subtype": "checking",
                "current_balance": 100.00,
                "available_balance": 90.00,
            }
        ],
    )

    monkeypatch.setattr(
        "app.plaid_link_server.register_plaid_accounts",
        lambda item_id, plaid_accounts: (
            captured.update(
                {
                    "registered_item_id": item_id,
                    "registered_accounts": (
                        plaid_accounts
                    ),
                }
            )
            or [1]
        ),
    )

    client = app.test_client()

    response = client.post(
        "/api/exchange_public_token",
        json={
            "public_token": "public-test-token"
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["item_id"] == "item-link-test"

    assert (
        captured["item_id"]
        == "item-link-test"
    )

    assert (
        captured["registered_item_id"]
        == "item-link-test"
    )

    assert len(
        captured["registered_accounts"]
    ) == 1