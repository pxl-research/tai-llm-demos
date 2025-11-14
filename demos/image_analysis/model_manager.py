import sys
from typing import Dict, List, Any

import streamlit as st

from app_config import DEFAULT_MODEL, OPENROUTER_API_KEY
from utils import (
    call_openrouter_api,
    load_model_scores,
    sort_models_by_score
)

sys.path.append('../../')
from demos.components.open_router.or_model_filtering import get_models


def load_and_sort_models():
    """Load models from OpenRouter API and sort them by score"""
    # Only load models if not already loaded
    if not st.session_state.all_models_data:
        # Get models that support image processing
        df_models = get_models(tools_only=False,
                               image_only=True,
                               min_context=16000,
                               max_completion_price=20,
                               max_prompt_price=10,
                               skip_free=True,
                               skip_experimental=True)

        models = df_models.to_dict('records')
        st.session_state.all_models_data = models
        st.session_state.total_image_capable_models = len(models)

        # Load model scores from CSV
        scores = load_model_scores()
        st.session_state.model_scores = scores

        if models and scores:
            # Sort models by their performance scores
            sorted_models, matched_count = sort_models_by_score(models, scores)
            st.session_state.all_models_data = sorted_models
            st.session_state.matched_models_count = matched_count

            # Set default model
            set_default_model(sorted_models)
        elif models:
            # No scores available, but we have models
            set_default_model(models)
            st.warning("Could not load model scores. Models are not sorted by capability.")
        else:
            st.error("No image-capable models found. Please check your internet connection or OpenRouter API.")


def set_default_model(models: List[Dict[str, Any]]):
    """Set the default model from available options"""
    # Try to use the preferred default model if available
    if any(model['full_model_name'] == DEFAULT_MODEL for model in models):
        st.session_state.selected_model_id = DEFAULT_MODEL
    # Otherwise use the first available model
    elif models:
        st.session_state.selected_model_id = models[0]['full_model_name']


def update_selected_model():
    """Callback when user selects a different model"""
    st.session_state.selected_model_id = st.session_state.model_selector


def prepare_api_messages(prompt: str) -> List[Dict[str, Any]]:
    """Create API message format from chat history and current prompt"""
    api_messages = []

    # Add chat history
    for msg in st.session_state.messages:
        if msg["type"] == "text":
            api_messages.append({
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            })

    # Create content for current message
    current_content = [{"type": "text", "text": prompt}]

    # Add image if available
    if "current_image_message" in st.session_state:
        current_content.insert(0, st.session_state.current_image_message)
        del st.session_state.current_image_message  # Clear after use

    # Add current message
    api_messages.append({"role": "user", "content": current_content})

    return api_messages


def call_model_api(messages: List[Dict[str, Any]]):
    """Call the selected model with the prepared messages"""
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Call API
            response = call_openrouter_api(
                st.session_state.selected_model_id,
                messages,
                OPENROUTER_API_KEY
            )

            # Process response
            if response and response.get("choices"):
                # Extract and display message
                assistant_message = response["choices"][0]["message"]["content"]
                st.markdown(assistant_message)

                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": assistant_message
                })
            else:
                # Handle error
                st.error("Failed to get a response from the model.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": "Error: Could not get a response."
                })
