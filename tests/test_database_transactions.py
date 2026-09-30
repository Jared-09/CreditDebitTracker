import pytest

from app.database import (
    database_transaction,
    get_connection,
)


def test_database_transaction_commits(test_database):
    """Successful transactions should save their changes."""

    with database_transaction() as connection:
        connection.execute(
            """
            INSERT INTO accounts (
                name,
                institution,
                account_type
            )
            VALUES (?, ?, ?)
            """,
            (
                "Test Credit Card",
                "Test Bank",
                "credit_card",
            ),
        )

    # Use a new connection to verify the data was saved.
    connection = get_connection()

    accounts = connection.execute(
        "SELECT name FROM accounts"
    ).fetchall()

    connection.close()

    assert len(accounts) == 1
    assert accounts[0][0] == "Test Credit Card"


def test_database_transaction_rolls_back(test_database):
    """Failed transactions should undo their changes."""

    with pytest.raises(ValueError):
        with database_transaction() as connection:
            connection.execute(
                """
                INSERT INTO accounts (
                    name,
                    institution,
                    account_type
                )
                VALUES (?, ?, ?)
                """,
                (
                    "Test Credit Card",
                    "Test Bank",
                    "credit_card",
                ),
            )

            # Simulate a failure before the transaction finishes.
            raise ValueError("Simulated database failure")

    # Verify the account was NOT saved.
    connection = get_connection()

    accounts = connection.execute(
        "SELECT name FROM accounts"
    ).fetchall()

    connection.close()

    assert accounts == []