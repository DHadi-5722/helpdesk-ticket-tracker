"""Centralize SQLite connections and the explicit database reset command."""

import sqlite3
from pathlib import Path


# Resolve paths relative to this file so the app works from any working directory.
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "helpdesk.db"
SCHEMA = BASE_DIR / "schema.sql"


def get_connection():
    """Open the project database with rows accessible by column name; the caller must close it."""
    connection = sqlite3.connect(DATABASE)
    # Named columns make templates and route code easier to read than numeric indexes.
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Rebuild the database from schema.sql. WARNING: this deletes all existing tickets."""
    connection = get_connection()

    with open(SCHEMA, "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())

    connection.commit()
    connection.close()

    print("HelpDesk Lite database initialized successfully.")


if __name__ == "__main__":
    initialize_database()