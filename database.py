import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "helpdesk.db"
SCHEMA = BASE_DIR / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    with open(SCHEMA, "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    connection.commit()
    connection.close()

    print("HelpDesk Lite database initialized successfully.")


if __name__ == "__main__":
    initialize_database()