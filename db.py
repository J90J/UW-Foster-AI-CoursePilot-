import json
import sqlite3
from pathlib import Path
from typing import Any

from config import DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    pages INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    text TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
"""


def connect(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def encode_vector(vector: list[float]) -> str:
    return json.dumps(vector, separators=(",", ":"))


def decode_vector(raw: str) -> list[float]:
    value: Any = json.loads(raw)
    return [float(item) for item in value]

