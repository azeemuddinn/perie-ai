import sqlite3
from contextlib import contextmanager

DB_NAME = "perie_ai.db"

def init_db():
    """Initializes the SQLite database with topics and runs tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table to track fetched news items and avoid duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            source TEXT,
            snippet TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    # Table to log daily agent selections and evaluation scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            selected_topic_id INTEGER,
            evaluation_score REAL,
            summary TEXT,
            FOREIGN KEY (selected_topic_id) REFERENCES topics(id)
        )
    """)
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for safe database connections and automatic closing."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()