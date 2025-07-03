import sqlite3


class SQLiteConnection:
    """Context manager for SQLite connections."""

    def __init__(self, db_path: str):
        """Initialize the connection."""
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """Enter the context and establish a connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and close the connection."""
        if self.conn:
            self.conn.close()
