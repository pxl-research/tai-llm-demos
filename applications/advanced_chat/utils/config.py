"""
Configuration module for Advanced Chat application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
APP_ROOT = Path(__file__).parent.parent
DATA_DIR = APP_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# User-specific path functions
def get_user_data_dir(username: str) -> Path:
    """Get the data directory for a specific user."""
    return DATA_DIR / "users" / username


def get_user_conversations_dir(username: str) -> Path:
    """Get the conversations directory for a specific user."""
    return get_user_data_dir(username) / "conversations"


def get_user_rag_db_path(username: str) -> Path:
    """Get the RAG database path for a specific user."""
    return get_user_data_dir(username) / "rag_db"


def get_user_settings_path(username: str) -> Path:
    """Get the settings file path for a specific user."""
    return get_user_data_dir(username) / "settings.json"

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'anthropic/claude-haiku-4.5')

# Google Search Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Authentication
AUTH_FILE = APP_ROOT / ".passwd"

# UI Configuration
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048

# System instruction
SYSTEM_INSTRUCTION = {
    'role': 'system',
    'content': (
        'You are a helpful assistant. '
        'Be concise, but include all relevant details. '
        'Always think step by step. '
        'If unsure, state your assumptions. '
        'You can answer using Markdown syntax. '
        'You have a lot of tools at your disposal, think about when to use them. '
        'When using an external source, always include the reference.'
    )
}
