import sqlite3
from contextlib import contextmanager
from pathlib import Path


DATABASE_PATH = Path("data") / "credit_card_control.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def database_transaction():
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
                current_balance REAL,
                account_role TEXT NOT NULL DEFAULT 'other'
            )
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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS plaid_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL UNIQUE,
                access_token TEXT NOT NULL,
                sync_cursor TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS plaid_item_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id)
                    REFERENCES accounts(id),
                FOREIGN KEY (item_id)
                    REFERENCES plaid_items(item_id),
                UNIQUE(item_id, account_id)
            )
            """
        )

        # Migrate older databases that were created before
        # current_balance and account_role were added.

        account_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(accounts)"
            ).fetchall()
        }

        if "current_balance" not in account_columns:
            connection.execute(
                """
                ALTER TABLE accounts
                ADD COLUMN current_balance REAL
                """
            )

        if "account_role" not in account_columns:
            connection.execute(
                """
                ALTER TABLE accounts
                ADD COLUMN account_role TEXT NOT NULL DEFAULT 'other'
                """
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()