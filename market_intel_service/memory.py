import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Tuple

from .config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, created_at);
"""

@contextmanager
def _conn():
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(settings.db_path)
    try:
        yield con
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript(SCHEMA)
        con.commit()


def append_messages(session_id: str, messages: List[Tuple[str, str]]) -> None:
    """Append a list of (role, content) to a session."""
    if not messages:
        return
    with _conn() as con:
        con.executemany(
            "INSERT INTO messages(session_id, role, content) VALUES (?, ?, ?)",
            [(session_id, role, content) for role, content in messages],
        )
        con.commit()


def fetch_context(session_id: str, limit: int) -> List[Tuple[str, str]]:
    """Return last N messages for session ordered ascending by time."""
    with _conn() as con:
        cur = con.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (session_id, limit),
        )
        rows = cur.fetchall()
    rows.reverse()
    return [(r[0], r[1]) for r in rows]


def clear_session(session_id: str) -> int:
    with _conn() as con:
        cur = con.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        con.commit()
        return cur.rowcount

