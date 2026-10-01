from app.database import get_connection


def test_plaid_items_table_exists(
    test_database,
):
    connection = get_connection()

    try:
        columns = connection.execute(
            """
            PRAGMA table_info(plaid_items)
            """
        ).fetchall()

    finally:
        connection.close()

    column_names = {
        column[1]
        for column in columns
    }

    assert column_names == {
        "id",
        "item_id",
        "access_token",
        "sync_cursor",
        "created_at",
        "updated_at",
    }