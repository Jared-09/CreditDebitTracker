from app.database import get_connection


def save_plaid_item(
    item_id,
    access_token,
    sync_cursor=None,
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO plaid_items (
                item_id,
                access_token,
                sync_cursor
            )
            VALUES (?, ?, ?)

            ON CONFLICT(item_id)
            DO UPDATE SET
                access_token = excluded.access_token,
                sync_cursor = excluded.sync_cursor,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                item_id,
                access_token,
                sync_cursor,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_plaid_item(item_id):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                item_id,
                access_token,
                sync_cursor
            FROM plaid_items
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None

        return {
            "item_id": row[0],
            "access_token": row[1],
            "sync_cursor": row[2],
        }

    finally:
        connection.close()


def update_plaid_cursor(
    item_id,
    sync_cursor,
):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE plaid_items
            SET sync_cursor = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE item_id = ?
            """,
            (
                sync_cursor,
                item_id,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def link_plaid_item_to_account(
    item_id,
    account_id,
):
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO plaid_items (
                item_id,
                access_token
            )
            VALUES (?, ?)
            """,
            (
                item_id,
                "",
            ),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO plaid_item_accounts (
                item_id,
                account_id
            )
            VALUES (?, ?)
            """,
            (
                item_id,
                account_id,
            ),
        )

        connection.commit()

    finally:
        connection.close()


def link_plaid_account_to_local_account(
    plaid_account_id,
    account_id,
    item_id=None,
):
    """
    Associate a specific Plaid account with a local
    application account.

    The Plaid account ID identifies the individual
    account within a Plaid Item.

    When item_id is supplied, also create the
    Plaid Item -> local account relationship used
    by the daily synchronization process.
    """

    connection = get_connection()

    try:
        account = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()

        if account is None:
            raise ValueError(
                f"Account {account_id} was not found."
            )

        existing = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE plaid_account_id = ?
              AND id != ?
            """,
            (
                plaid_account_id,
                account_id,
            ),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                "Plaid account "
                f"{plaid_account_id} is already linked "
                f"to local account {existing[0]}."
            )

        if item_id is not None:
            plaid_item = connection.execute(
                """
                SELECT item_id
                FROM plaid_items
                WHERE item_id = ?
                """,
                (item_id,),
            ).fetchone()

            if plaid_item is None:
                raise ValueError(
                    f"Plaid Item {item_id} was not found."
                )

        connection.execute(
            """
            UPDATE accounts
            SET plaid_account_id = ?
            WHERE id = ?
            """,
            (
                plaid_account_id,
                account_id,
            ),
        )

        if item_id is not None:
            connection.execute(
                """
                INSERT OR IGNORE INTO plaid_item_accounts (
                    item_id,
                    account_id
                )
                VALUES (?, ?)
                """,
                (
                    item_id,
                    account_id,
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_account_plaid_item(
    item_id,
):
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT account_id
            FROM plaid_item_accounts
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None

        return row[0]

    finally:
        connection.close()


def get_all_plaid_account_links():
    """
    Return all Plaid Item -> Account connections.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                item_id,
                account_id
            FROM plaid_item_accounts
            """
        ).fetchall()

        return [
            {
                "item_id": row[0],
                "account_id": row[1],
            }
            for row in rows
        ]

    finally:
        connection.close()