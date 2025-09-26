import os
import sqlite3
from typing import Iterable, Tuple, Optional
from .config import get_settings

DB_PATH = get_settings().database_path
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                user_id TEXT PRIMARY KEY,
                persona TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def set_persona(user_id: str, persona: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_state(user_id, persona) VALUES(?, ?)\n"
            "ON CONFLICT(user_id) DO UPDATE SET persona=excluded.persona, updated_at=CURRENT_TIMESTAMP",
            (user_id, persona),
        )
        conn.commit()


def get_persona(user_id: str) -> Optional[str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT persona FROM user_state WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        return row["persona"] if row else None


def add_message(user_id: str, role: str, content: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages(user_id, role, content) VALUES(?, ?, ?)",
            (user_id, role, content),
        )
        conn.commit()


def get_recent_messages(user_id: str, limit: int = 12) -> Iterable[Tuple[str, str]]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = cur.fetchall()
        # Return in chronological order
        return [(r["role"], r["content"]) for r in reversed(rows)]
