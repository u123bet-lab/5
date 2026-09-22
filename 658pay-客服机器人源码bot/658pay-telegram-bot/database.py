"""SQLite persistence for customers and administrator reply routing."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS customers (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT NOT NULL,
                    first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    blocked INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS admin_message_map (
                    admin_chat_id INTEGER NOT NULL,
                    admin_message_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (admin_chat_id, admin_message_id)
                );
                CREATE INDEX IF NOT EXISTS idx_message_map_customer
                ON admin_message_map(customer_id);
            """)

    def upsert_customer(self, telegram_id: int, username: Optional[str], full_name: str) -> None:
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO customers (telegram_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username=excluded.username,
                    full_name=excluded.full_name,
                    last_seen=CURRENT_TIMESTAMP
            """, (telegram_id, username, full_name))

    def map_admin_message(self, admin_chat_id: int, admin_message_id: int, customer_id: int) -> None:
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO admin_message_map
                (admin_chat_id, admin_message_id, customer_id) VALUES (?, ?, ?)
            """, (admin_chat_id, admin_message_id, customer_id))

    def customer_for_admin_message(self, admin_chat_id: int, admin_message_id: int) -> Optional[int]:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT customer_id FROM admin_message_map
                WHERE admin_chat_id=? AND admin_message_id=?
            """, (admin_chat_id, admin_message_id)).fetchone()
        return int(row["customer_id"]) if row else None

    def is_blocked(self, telegram_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT blocked FROM customers WHERE telegram_id=?", (telegram_id,)).fetchone()
        return bool(row and row["blocked"])

    def set_blocked(self, telegram_id: int, blocked: bool) -> bool:
        with self._connect() as conn:
            cursor = conn.execute("UPDATE customers SET blocked=? WHERE telegram_id=?", (int(blocked), telegram_id))
        return cursor.rowcount > 0

    def user_count(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0])

    def broadcast_recipients(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT telegram_id FROM customers WHERE blocked=0 ORDER BY telegram_id").fetchall()
        return [int(row["telegram_id"]) for row in rows]
