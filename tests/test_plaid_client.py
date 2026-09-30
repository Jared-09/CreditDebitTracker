from plaid.api_client import ApiClient

from app.plaid import create_plaid_client


def test_create_plaid_client(monkeypatch):
    monkeypatch.setenv(
        "PLAID_CLIENT_ID",
        "test_client_id",
    )
    monkeypatch.setenv(
        "PLAID_SECRET",
        "test_secret",
    )
    monkeypatch.setenv(
        "PLAID_ENV",
        "sandbox",
    )

    client = create_plaid_client()

    assert isinstance(
        client.api_client,
        ApiClient,
    )