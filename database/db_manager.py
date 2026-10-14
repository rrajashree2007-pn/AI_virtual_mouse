"""
db_manager.py
Thin SQLite wrapper providing persistence for:
- app settings (key/value)
- custom gesture -> action bindings
- analytics events (gesture usage, mode switches, session summaries)
"""

import sqlite3
import json
import time
import os


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS gesture_bindings (
                    gesture_name TEXT PRIMARY KEY,
                    action_name TEXT,
                    mode TEXT
                );

                CREATE TABLE IF NOT EXISTS gesture_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesture_name TEXT,
                    timestamp REAL
                );

                CREATE TABLE IF NOT EXISTS mode_switch_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode_name TEXT,
                    timestamp REAL
                );

                CREATE TABLE IF NOT EXISTS session_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_json TEXT,
                    timestamp REAL
                );
                """
            )

    # ---------------- settings ----------------
    def set_setting(self, key, value):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, json.dumps(value)),
            )

    def get_setting(self, key, default=None):
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return json.loads(row[0]) if row else default

    # ---------------- gesture bindings ----------------
    def bind_gesture(self, gesture_name, action_name, mode="default"):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO gesture_bindings (gesture_name, action_name, mode) VALUES (?, ?, ?) "
                "ON CONFLICT(gesture_name) DO UPDATE SET action_name=excluded.action_name, mode=excluded.mode",
                (gesture_name, action_name, mode),
            )

    def get_bindings(self, mode=None):
        with self._connect() as conn:
            if mode:
                rows = conn.execute(
                    "SELECT gesture_name, action_name FROM gesture_bindings WHERE mode = ?", (mode,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT gesture_name, action_name FROM gesture_bindings").fetchall()
            return {g: a for g, a in rows}

    # ---------------- analytics ----------------
    def log_gesture_event(self, gesture_name):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO gesture_events (gesture_name, timestamp) VALUES (?, ?)",
                (gesture_name, time.time()),
            )

    def log_mode_switch(self, mode_name):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO mode_switch_events (mode_name, timestamp) VALUES (?, ?)",
                (mode_name, time.time()),
            )

    def log_session_summary(self, summary_dict):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO session_summaries (summary_json, timestamp) VALUES (?, ?)",
                (json.dumps(summary_dict), time.time()),
            )

    def get_gesture_frequency(self, since_timestamp=0):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT gesture_name, COUNT(*) FROM gesture_events "
                "WHERE timestamp >= ? GROUP BY gesture_name ORDER BY COUNT(*) DESC",
                (since_timestamp,),
            ).fetchall()
            return dict(rows)

    def get_recent_sessions(self, limit=10):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT summary_json, timestamp FROM session_summaries "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [{"summary": json.loads(s), "timestamp": t} for s, t in rows]
