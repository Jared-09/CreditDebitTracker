from app.database import get_connection, initialize_database


def main():
    initialize_database()

    connection = get_connection()

    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

    connection.close()

    print("Database tables:", tables)


if __name__ == "__main__":
    main()