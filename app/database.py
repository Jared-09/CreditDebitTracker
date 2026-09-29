import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data") / "credit_card_control.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create the database tables if they do not already exist."""
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            institution TEXT NOT NULL,
            account_type TEXT NOT NULL,
            last_four TEXT,
            plaid_account_id TEXT UNIQUE,
            active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    connection.commit()
    connection.close()