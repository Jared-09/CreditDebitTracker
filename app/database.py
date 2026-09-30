import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = Path("data") / "credit_card_control.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def database_transaction():
    """
    Manage a database transaction.
    Commit all changes if successful.
    Roll back all changes if an error occurs.
    Always close the connection.
    """
    connection = get_connection()

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database():
    """Create the database tables and apply simple schema upgrades."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                institution TEXT NOT NULL,
                account_type TEXT NOT NULL,
                last_four TEXT,
                plaid_account_id TEXT UNIQUE,
                active INTEGER NOT NULL DEFAULT 1,
                current_balance REAL
            )
            """
        )

        # Existing databases created before current_balance was added
        # need a small schema upgrade.
        account_columns = connection.execute(
            "PRAGMA table_info(accounts)"
        ).fetchall()

        column_names = {
            column[1]
            for column in account_columns
        }

        if "current_balance" not in column_names:
            connection.execute(
                """
                ALTER TABLE accounts
                ADD COLUMN current_balance REAL
                """
            )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                plaid_transaction_id TEXT UNIQUE,
                pending_transaction_id TEXT,
                merchant_name TEXT,
                description TEXT,
                transaction_date TEXT NOT NULL,
                plaid_amount REAL,
                manual_amount REAL,
                pending INTEGER NOT NULL DEFAULT 0,
                transaction_type TEXT NOT NULL DEFAULT 'purchase',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()