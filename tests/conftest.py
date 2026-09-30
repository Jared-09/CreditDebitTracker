import pytest

import app.database as database


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Create a fresh temporary database for a test."""

    temporary_database = tmp_path / "test_credit_card_control.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        temporary_database,
    )

    database.initialize_database()

    return temporary_database