import base64
import sys
from typing import Dict, List, Any, Tuple

import pandas as pd
import requests
from thefuzz import fuzz

sys.path.append('../../')
from components.open_router.or_model_filtering import get_models


def load_model_scores(csv_path="./lmarena_vision_250616.csv") -> Dict[str, float]:
    """
    Loads model scores from a CSV file and returns a dictionary mapping
    model identifiers to their scores.
    """
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        score_map = {}
        for _, row in df.iterrows():
            organization = str(row["Organization"]).lower()
            model_name = str(row["Model"])
            score = float(row["Score"])
            # Construct key as "organization/model"
            key = f"{organization}/{model_name}"
            score_map[key] = score
        return score_map
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return {}
    except Exception as e:
        print(f"Error loading model scores from CSV: {e}")
        return {}


def sort_models_by_score(model_objects: List[Dict[str, Any]],
                         score_map: Dict[str, float],
                         fuzzy_match_threshold: int = 80
                         ) -> Tuple[List[Dict[str, Any]], int]:
    """
    Sorts models by performance score and returns the sorted list and count of matched models.
    Uses fuzzy matching when exact model ID matches aren't found in the score map.
    """
    scored_models = []
    matched_count = 0

    for model in model_objects:
        model_id = model['full_model_name']
        # Try direct match first
        score = score_map.get(model_id.lower(), None)

        # If no direct match, try fuzzy matching
        if score is None:
            best_match = None
            best_score = 0

            for csv_key in score_map.keys():
                match_score = fuzz.ratio(model_id.lower(), csv_key)
                if match_score > best_score:
                    best_score = match_score
                    best_match = csv_key

            # Use fuzzy match if it's good enough
            if best_match and best_score >= fuzzy_match_threshold:
                score = score_map[best_match]
                matched_count += 1
            else:
                score = float('-inf')
        else:
            matched_count += 1

        # Store the score in the model object for UI display
        model["lm_arena_score"] = score if score != float('-inf') else "N/A"
        scored_models.append((score, model))

    # Sort by score (highest first)
    scored_models.sort(key=lambda x: x[0], reverse=True)
    sorted_models = [model for _, model in scored_models]

    return sorted_models, matched_count


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


if __name__ == '__main__':
    # Test the functions
    print("--- Testing get_image_capable_models ---")
    models = get_models(tools_only=False,
                        image_only=True,
                        min_context=16000,
                        max_completion_price=20,
                        max_prompt_price=10,
                        skip_free=True,
                        skip_experimental=True)

    all_image_capable_models = models.to_dict('records')
    if all_image_capable_models:
        print(f"Found {len(all_image_capable_models)} image-capable models.")
    else:
        print("No image-capable models found or an error occurred.")

    print("\n--- Testing load_model_scores ---")
    model_scores_map = load_model_scores()
    if model_scores_map:
        print(f"Loaded {len(model_scores_map)} scores from CSV.")
    else:
        print("No model scores loaded from CSV or an error occurred.")

    print("\n--- Testing sort_models_by_score ---")
    if all_image_capable_models and model_scores_map:
        sorted_models, matched_count = sort_models_by_score(all_image_capable_models, model_scores_map)
        print(f"Sorted {len(sorted_models)} models. Matched {matched_count} models with scores from CSV.")
    else:
        print("Skipping model sorting test due to missing models or scores.")
