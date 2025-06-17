import base64
import json

import pandas as pd
import requests


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

        filtered_models.append(model['id'])

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


def sort_models_by_score(model_ids, score_map):
    """
    Sorts a list of OpenRouter model IDs based on scores from the score_map.
    Models not found in the score_map will be placed at the bottom.
    Returns the sorted list of model IDs and the count of matched models.
    """
    scored_models = []
    matched_count = 0

    for model_id in model_ids:
        # OpenRouter model_id format: "organization/model_name"
        # Try to match directly with the score_map key
        score = score_map.get(model_id.lower(),
                              float('-inf'))  # Use .lower() for consistency if model_id also has organization part

        if score != float('-inf'):
            matched_count += 1
        scored_models.append((score, model_id))

    # Sort in descending order by score
    scored_models.sort(key=lambda x: x[0], reverse=True)

    sorted_model_ids = [model_id for score, model_id in scored_models]

    return sorted_model_ids, matched_count


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
    # Example usage for get_image_capable_models:
    print("Fetching image-capable models...")
    models = get_image_capable_models()
    if models:
        print("Found image-capable models:")
        for model_id in models:
            print(f"- {model_id}")
    else:
        print("No image-capable models found or an error occurred.")
