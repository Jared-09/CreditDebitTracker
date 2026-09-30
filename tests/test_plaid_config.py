import pytest

from app.plaid import get_plaid_config


def test_get_plaid_config(monkeypatch):
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

    config = get_plaid_config()

    assert config["client_id"] == "test_client_id"
    assert config["secret"] == "test_secret"
    assert config["environment"] == "sandbox"


def test_missing_plaid_client_id_is_rejected(
    monkeypatch,
):
    monkeypatch.delenv(
        "PLAID_CLIENT_ID",
        raising=False,
    )
    monkeypatch.setenv(
        "PLAID_SECRET",
        "test_secret",
    )
    monkeypatch.setenv(
        "PLAID_ENV",
        "sandbox",
    )

    with pytest.raises(
        ValueError,
        match="PLAID_CLIENT_ID is not configured",
    ):
        get_plaid_config()


def test_missing_plaid_secret_is_rejected(
    monkeypatch,
):
    monkeypatch.setenv(
        "PLAID_CLIENT_ID",
        "test_client_id",
    )
    monkeypatch.delenv(
        "PLAID_SECRET",
        raising=False,
    )
    monkeypatch.setenv(
        "PLAID_ENV",
        "sandbox",
    )

    with pytest.raises(
        ValueError,
        match="PLAID_SECRET is not configured",
    ):
        get_plaid_config()


def test_invalid_plaid_environment_is_rejected(
    monkeypatch,
):
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
        "invalid",
    )

    with pytest.raises(
        ValueError,
        match="Invalid PLAID_ENV",
    ):
        get_plaid_config()