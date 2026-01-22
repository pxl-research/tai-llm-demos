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
CONVERSATIONS_DIR = DATA_DIR / "conversations"
RAG_DB_PATH = DATA_DIR / "rag_db"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
RAG_DB_PATH.mkdir(parents=True, exist_ok=True)

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
