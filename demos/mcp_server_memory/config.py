"""
Configuration settings for the MCP Memory Server.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database paths
DB_PATH = os.getenv("DB_PATH", "./memory_db")
SQLITE_PATH = os.path.join(DB_PATH, "memory.sqlite")
CHROMA_PATH = os.path.join(DB_PATH, "chroma")

# Collection names
MEMORY_COLLECTION = "memory_items"
TOPICS_COLLECTION = "topics"

# Other configuration
DEFAULT_MAX_RESULTS = 5
