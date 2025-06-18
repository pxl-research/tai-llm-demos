import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = 'google/gemini-2.0-flash-001'

# Price thresholds for highlighting expensive models (per million tokens)
PROMPT_PRICE_THRESHOLD = 1.5
COMPLETION_PRICE_THRESHOLD = 7.5
IMAGE_PRICE_THRESHOLD = 7.5

# Session state keys
SESSION_KEYS = {
    "messages": [],
    "image_capable_models": [],
    "selected_model_id": None,
    "model_scores": {},
    "matched_models_count": 0,
    "last_uploaded_file_id": None,
    "all_models_data": [],
    "total_image_capable_models": 0,
}
