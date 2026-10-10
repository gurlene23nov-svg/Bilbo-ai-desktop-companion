from contextlib import contextmanager
import sqlite3
from pathlib import Path
from datetime import datetime


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATABASE_PATH = DATA_DIR / "bilbo.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                speaker TEXT NOT NULL,
                message TEXT NOT NULL,
                mood TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def save_message(speaker, message, mood=None):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO messages (speaker, message, mood, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (speaker, message, mood, datetime.now().isoformat(timespec="seconds")),
        )


def get_recent_messages(limit=50):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT speaker, message, mood, created_at
            FROM messages
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


# Backward-compatible aliases for the API layer.
def add_message(speaker, message, mood=None):
    save_message(speaker, message, mood)


def get_history(limit=50):
    return get_recent_messages(limit)