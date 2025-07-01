"""
SQLite database manager for the MCP Memory Server.
"""

import os
import sqlite3
import sys
from typing import List, Dict, Any, Optional

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import using local path
from config import SQLITE_PATH
from utils.helpers import timestamp


class SQLiteManager:
    """Manager for SQLite database operations."""

    def __init__(self):
        """Initialize the SQLite manager."""
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

    def get_connection(self):
        """Get a connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: A connection to the database
        """
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self, reset: bool = False) -> bool:
        """Initialize the SQLite database.
        
        Args:
            reset: Whether to reset the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if reset:
                cursor.execute("DROP TABLE IF EXISTS memory_items")
                cursor.execute("DROP TABLE IF EXISTS topics")
                cursor.execute("DROP TABLE IF EXISTS summaries")  # New: Drop summaries table

            # Create tables if they don't exist
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS memory_items
                           (
                               id
                               TEXT
                               PRIMARY
                               KEY,
                               content
                               TEXT
                               NOT
                               NULL,
                               topic
                               TEXT
                               NOT
                               NULL,
                               tags
                               TEXT,
                               created_at
                               TEXT
                               NOT
                               NULL,
                               updated_at
                               TEXT
                               NOT
                               NULL,
                               version
                               INTEGER
                               DEFAULT
                               1,
                               is_current
                               BOOLEAN
                               DEFAULT
                               1,
                               importance
                               REAL
                               DEFAULT
                               0.5
                           )
                           """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS topics
                           (
                               name
                               TEXT
                               PRIMARY
                               KEY,
                               description
                               TEXT,
                               created_at
                               TEXT
                               NOT
                               NULL,
                               item_count
                               INTEGER
                               DEFAULT
                               0
                           )
                           """)

            # New: Create summaries table
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS summaries
                           (
                               id
                               TEXT
                               PRIMARY
                               KEY,
                               memory_id
                               TEXT
                               NOT
                               NULL,
                               summary_type
                               TEXT
                               NOT
                               NULL,
                               summary_text
                               TEXT
                               NOT
                               NULL,
                               created_at
                               TEXT
                               NOT
                               NULL,
                               updated_at
                               TEXT
                               NOT
                               NULL,
                               FOREIGN
                               KEY
                           (
                               memory_id
                           ) REFERENCES memory_items
                           (
                               id
                           ) ON DELETE CASCADE
                               )
                           """)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error initializing SQLite database: {e}")
            return False

    def store_summary(self, summary_id: str, memory_id: str, summary_type: str, summary_text: str) -> bool:
        """Store a summary item in the database.

        Args:
            summary_id: Unique ID for the summary item
            memory_id: The ID of the memory item this summary belongs to
            summary_type: The type of summary (e.g., 'abstractive_medium')
            summary_text: The summary content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO summaries
                    (id, memory_id, summary_type, summary_text, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (summary_id, memory_id, summary_type, summary_text, now, now)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error storing summary in SQLite: {e}")
            return False

    def get_summary(self, memory_id: str, summary_type: str) -> Optional[Dict[str, Any]]:
        """Get a summary item by memory ID and summary type.

        Args:
            memory_id: The ID of the memory to retrieve summary for
            summary_type: The type of summary to retrieve

        Returns:
            Optional[Dict[str, Any]]: The summary item or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM summaries WHERE memory_id = ? AND summary_type = ?",
                (memory_id, summary_type)
            )
            item = cursor.fetchone()
            conn.close()

            if not item:
                return None

            return {
                "id": item["id"],
                "memory_id": item["memory_id"],
                "summary_type": item["summary_type"],
                "summary_text": item["summary_text"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"]
            }

        except Exception as e:
            print(f"Error getting summary from SQLite: {e}")
            return None

    def get_summary_by_id(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary item by its unique ID.

        Args:
            summary_id: The unique ID of the summary to retrieve

        Returns:
            Optional[Dict[str, Any]]: The summary item or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM summaries WHERE id = ?",
                (summary_id,)
            )
            item = cursor.fetchone()
            conn.close()

            if not item:
                return None

            return {
                "id": item["id"],
                "memory_id": item["memory_id"],
                "summary_type": item["summary_type"],
                "summary_text": item["summary_text"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"]
            }

        except Exception as e:
            print(f"Error getting summary by ID from SQLite: {e}")
            return None

    def update_summary(self, summary_id: str, new_summary_text: str) -> bool:
        """Update an existing summary item.

        Args:
            summary_id: The ID of the summary to update
            new_summary_text: The new summary content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE summaries
                SET summary_text = ?,
                    updated_at   = ?
                WHERE id = ?
                """,
                (new_summary_text, now, summary_id)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating summary in SQLite: {e}")
            return False

    def delete_summaries(self, memory_id: str) -> bool:
        """Delete all summaries associated with a memory ID.

        Args:
            memory_id: The ID of the memory whose summaries to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM summaries WHERE memory_id = ?", (memory_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error deleting summaries from SQLite: {e}")
            return False

    def store_memory(self, memory_id: str, content: str, topic: str, tags: List[str]) -> bool:
        """Store a memory item in the database.
        
        Args:
            memory_id: Unique ID for the memory item
            content: The content to store
            topic: The topic category
            tags: List of tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if topic exists, create if not
            cursor.execute("SELECT * FROM topics WHERE name = ?", (topic,))
            topic_exists = cursor.fetchone()

            if not topic_exists:
                cursor.execute(
                    "INSERT INTO topics (name, created_at, item_count) VALUES (?, ?, ?)",
                    (topic, now, 1)
                )
            else:
                cursor.execute(
                    "UPDATE topics SET item_count = item_count + 1 WHERE name = ?",
                    (topic,)
                )

            # Store the memory item
            cursor.execute(
                """
                INSERT INTO memory_items
                    (id, content, topic, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (memory_id, content, topic, ",".join(tags), now, now)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error storing memory in SQLite: {e}")
            return False

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory item by ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The memory item or None if not found
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memory_items WHERE id = ?", (memory_id,))
            item = cursor.fetchone()
            conn.close()

            if not item:
                return None

            return {
                "id": item["id"],
                "content": item["content"],
                "topic": item["topic"],
                "tags": item["tags"].split(",") if item["tags"] else [],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "version": item["version"],
                "is_current": bool(item["is_current"]),
                "importance": item["importance"]
            }

        except Exception as e:
            print(f"Error getting memory from SQLite: {e}")
            return None

    def update_memory(self, memory_id: str, content: Optional[str] = None,
                      topic: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
        """Update a memory item.
        
        Args:
            memory_id: The ID of the memory to update
            content: New content (if updating)
            topic: New topic (if updating)
            tags: New tags (if updating)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get current item
            cursor.execute("SELECT * FROM memory_items WHERE id = ?", (memory_id,))
            current_item = cursor.fetchone()

            if not current_item:
                return False

            # Prepare updated values
            new_content = content if content is not None else current_item["content"]
            new_topic = topic if topic is not None else current_item["topic"]
            new_tags = ",".join(tags) if tags is not None else current_item["tags"]

            # Update topic counts if topic is changing
            if topic is not None and topic != current_item["topic"]:
                # Decrement old topic count
                cursor.execute(
                    "UPDATE topics SET item_count = item_count - 1 WHERE name = ?",
                    (current_item["topic"],)
                )

                # Check if new topic exists, create if not
                cursor.execute("SELECT * FROM topics WHERE name = ?", (topic,))
                new_topic_exists = cursor.fetchone()

                if not new_topic_exists:
                    cursor.execute(
                        "INSERT INTO topics (name, created_at, item_count) VALUES (?, ?, ?)",
                        (topic, now, 1)
                    )
                else:
                    cursor.execute(
                        "UPDATE topics SET item_count = item_count + 1 WHERE name = ?",
                        (topic,)
                    )

            # Update SQLite record
            cursor.execute(
                """
                UPDATE memory_items
                SET content    = ?,
                    topic      = ?,
                    tags       = ?,
                    updated_at = ?,
                    version    = version + 1
                WHERE id = ?
                """,
                (new_content, new_topic, new_tags, now, memory_id)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating memory in SQLite: {e}")
            return False

    def list_topics(self) -> List[Dict[str, Any]]:
        """List all topics in the database.
        
        Returns:
            List[Dict[str, Any]]: List of topics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM topics ORDER BY item_count DESC")
            topics = cursor.fetchall()
            conn.close()

            result = []
            for topic in topics:
                result.append({
                    "name": topic["name"],
                    "description": topic["description"],
                    "item_count": topic["item_count"],
                    "created_at": topic["created_at"]
                })

            return result

        except Exception as e:
            print(f"Error listing topics from SQLite: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get database status and statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get memory items count
            cursor.execute("SELECT COUNT(*) as count FROM memory_items")
            memory_count = cursor.fetchone()["count"]

            # Get topics count
            cursor.execute("SELECT COUNT(*) as count FROM topics")
            topics_count = cursor.fetchone()["count"]

            # Get top topics
            cursor.execute("SELECT name, item_count FROM topics ORDER BY item_count DESC LIMIT 5")
            top_topics = cursor.fetchall()

            # Get latest item
            cursor.execute("SELECT created_at FROM memory_items ORDER BY created_at DESC LIMIT 1")
            latest_item = cursor.fetchone()

            conn.close()

            return {
                "total_memories": memory_count,
                "total_topics": topics_count,
                "top_topics": [{"name": t["name"], "count": t["item_count"]} for t in top_topics],
                "latest_item_date": latest_item["created_at"] if latest_item else None
            }

        except Exception as e:
            print(f"Error getting status from SQLite: {e}")
            return {}

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item from the database.

        Args:
            memory_id: The ID of the memory to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Get the topic of the memory item before deleting
            cursor.execute("SELECT topic FROM memory_items WHERE id = ?", (memory_id,))
            item = cursor.fetchone()

            if not item:
                conn.close()
                return False  # Memory item not found

            topic = item["topic"]

            # Delete the memory item
            cursor.execute("DELETE FROM memory_items WHERE id = ?", (memory_id,))

            # Decrement the item_count for the associated topic
            cursor.execute(
                "UPDATE topics SET item_count = item_count - 1 WHERE name = ?",
                (topic,)
            )

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error deleting memory from SQLite: {e}")
            return False

    def delete_topic_if_empty(self, topic_name: str) -> bool:
        """Delete a topic if its item_count is 0.

        Args:
            topic_name: The name of the topic to delete.

        Returns:
            bool: True if the topic was deleted, False otherwise.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if topic exists and its item_count is 0
            cursor.execute("SELECT item_count FROM topics WHERE name = ?", (topic_name,))
            topic_info = cursor.fetchone()

            if not topic_info:
                conn.close()
                return False  # Topic not found

            if topic_info["item_count"] == 0:
                cursor.execute("DELETE FROM topics WHERE name = ?", (topic_name,))
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False  # Topic is not empty

        except Exception as e:
            print(f"Error deleting topic from SQLite: {e}")
            return False
