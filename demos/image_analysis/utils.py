import base64
import json

import pandas as pd
import requests
from thefuzz import fuzz


def get_image_capable_models():
    """
    Fetches all models from the OpenRouter API and filters them to identify
    those that explicitly support both "text" and "image" input modalities.
    Returns a list of the IDs of these suitable models.
    """
    models_url = 'https://openrouter.ai/api/v1/models'
    try:
        response = requests.get(models_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        model_list = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models from OpenRouter: {e}")
        return []

    filtered_models = []
    for model in model_list.get('data', []):
        # 1. Filter out beta / experimental / free models
        if 'beta' in model['id'] or '-exp' in model['id'] or ':free' in model['id']:
            continue

        # Check for image and text modalities
        architecture = model.get('architecture', {})
        input_modalities = architecture.get('input_modalities', [])
        if "text" not in input_modalities or "image" not in input_modalities:
            continue

        # 2. Filter out small context models (using 16000 as a threshold)
        context_length = model.get('context_length', 0)
        if context_length < 16000:
            continue

        # 3. Filter out models with high completion or prompt prices
        pricing = model.get('pricing', {})
        prompt_price = float(pricing.get('prompt', 0))
        completion_price = float(pricing.get('completion', 0))

        # Convert to price per million tokens for comparison
        prompt_price_per_million = prompt_price * 1000000
        completion_price_per_million = completion_price * 1000000

        if prompt_price_per_million >= 10 or completion_price_per_million >= 20:
            continue

        # Exclude truly free models as they are often rate-limited
        if prompt_price == 0:
            continue

        filtered_models.append(model) # Append the full model object

    return filtered_models


def load_model_scores(csv_path="./lmarena_vision_250616.csv"):
    """
    Loads model scores from a CSV file and returns a dictionary mapping
    "{organization_lowercase}/{model_name}" to their scores.
    """
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        score_map = {}
        for index, row in df.iterrows():
            organization = str(row["Organization"]).lower()
            model_name = str(row["Model"])
            score = row["Score"]
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


def sort_models_by_score(model_objects, score_map):
    """
    Sorts a list of OpenRouter model objects based on scores from the score_map.
    Models not found in the score_map will be placed at the bottom.
    Returns the sorted list of model objects and the count of matched models.
    """
    scored_models = []
    matched_count = 0
    FUZZY_MATCH_THRESHOLD = 80  # Define a threshold for fuzzy matching

    for model in model_objects:
        model_id = model['id']
        # OpenRouter model_id format: "organization/model_name"
        # 1. Try to match directly with the score_map key
        score = score_map.get(model_id.lower(), float('-inf'))

        if score != float('-inf'):
            matched_count += 1
            model["lm_arena_score"] = score if score != float('-inf') else "N/A"
            scored_models.append((score, model))
        else:
            # 2. If direct match fails, try fuzzy matching
            best_fuzzy_score = float('-inf')
            best_matched_csv_key = None

            for csv_key in score_map.keys():
                # Use token_set_ratio for robust fuzzy matching
                current_fuzzy_score = fuzz.token_set_ratio(model_id.lower(), csv_key)
                if current_fuzzy_score > best_fuzzy_score:
                    best_fuzzy_score = current_fuzzy_score
                    best_matched_csv_key = csv_key
            
            if best_fuzzy_score >= FUZZY_MATCH_THRESHOLD and best_matched_csv_key:
                score = score_map[best_matched_csv_key]
                matched_count += 1
            
            # Assign score to the model object
            model["lm_arena_score"] = score if score != float('-inf') else "N/A"
            scored_models.append((score, model)) # Append (score, model_object) tuple

    # Sort in descending order by score
    scored_models.sort(key=lambda x: x[0], reverse=True)

    sorted_model_objects = [model for score, model in scored_models]

    return sorted_model_objects, matched_count


def encode_image_to_base64(image_file):
    """
    Encodes an image file (from Streamlit's file uploader) to a base64 data URL.
    """
    if image_file is None:
        return None

    # Read the image bytes
    image_bytes = image_file.read()

    # Determine the MIME type
    # Streamlit's file_uploader provides type, but we can also infer from magic bytes
    # For simplicity, we'll use the provided type or a common default
    mime_type = image_file.type if image_file.type else "image/jpeg"  # Default to jpeg if type is not provided

    # Encode to base64
    base64_encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    # Construct data URL
    data_url = f"data:{mime_type};base64,{base64_encoded_image}"
    return data_url


def call_openrouter_api(model_id, messages, api_key):
    """
    Calls the OpenRouter API with the given model, messages, and API key.
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
    print("--- Testing get_image_capable_models ---")
    all_image_capable_models = get_image_capable_models()
    if all_image_capable_models:
        print(f"Found {len(all_image_capable_models)} image-capable models (before sorting).")
        # Uncomment to print all models before sorting:
        # for model in all_image_capable_models:
        #     print(f"- {model['id']}")
    else:
        print("No image-capable models found or an error occurred.")

    print("\n--- Testing load_model_scores ---")
    model_scores_map = load_model_scores()
    if model_scores_map:
        print(f"Loaded {len(model_scores_map)} scores from CSV.")
        # Uncomment to print all loaded scores:
        # for key, score in model_scores_map.items():
        #     print(f"- {key}: {score}")
    else:
        print("No model scores loaded from CSV or an error occurred.")

    print("\n--- Testing sort_models_by_score ---")
    if all_image_capable_models and model_scores_map:
        sorted_models, matched_count = sort_models_by_score(all_image_capable_models, model_scores_map)
        print(f"\nSorted {len(sorted_models)} models. Matched {matched_count} models with scores from CSV.")
        print("Sorted Models (ID and LM Arena Score):")
        for model in sorted_models:
            print(f"- {model['id']} (Score: {model.get('lm_arena_score', 'N/A')})")
    else:
        print("Skipping model sorting test due to missing models or scores.")
