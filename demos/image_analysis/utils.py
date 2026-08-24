import base64
from typing import Dict, List, Any

import requests


def encode_image_to_base64(image_file) -> str:
    """
    Encodes an image file to a base64 data URL for API transmission.
    """
    if image_file is None:
        return None

    # Read the image bytes
    image_bytes = image_file.read()

    # Use the file's mime type or default to jpeg
    mime_type = image_file.type if hasattr(image_file, 'type') and image_file.type else "image/jpeg"

    # Encode to base64
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')

    # Return as data URL
    return f"data:{mime_type};base64,{base64_encoded}"


def call_openrouter_api(model_id: str, messages: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    """
    Calls the OpenRouter API with the specified model and messages.
    Returns the JSON response or None if an error occurs.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_id,
        "messages": messages,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return None
