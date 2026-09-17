from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import get_settings


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source TEXT NOT NULL,
                branch TEXT,
                mode TEXT NOT NULL,
                from_ref TEXT,
                to_ref TEXT,
                python_only INTEGER NOT NULL DEFAULT 0,
                effort TEXT NOT NULL DEFAULT 'medium',
                actor TEXT NOT NULL,
                actor_oid TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                error TEXT,
                files_reviewed INTEGER,
                comments INTEGER,
                total_tokens INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                elapsed TEXT,
                workspace_path TEXT,
                json_path TEXT,
                sarif_path TEXT
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                path TEXT NOT NULL,
                content TEXT NOT NULL,
                suggestion_code TEXT,
                existing_code TEXT,
                start_line INTEGER,
                end_line INTEGER,
                category TEXT,
                severity TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE TABLE IF NOT EXISTS job_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                line TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            );

            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                job_id TEXT,
                detail TEXT
            );
            """
        )


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def workspace_for(job_id: str) -> Path:
    path = get_settings().workspaces_dir / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path
