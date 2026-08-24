import sys
from typing import Dict, List, Any

import streamlit as st

from app_config import DEFAULT_MODEL, OPENROUTER_API_KEY
from utils import call_openrouter_api

sys.path.append('../../')
from components.lmarena.lmarena_scoring import load_lmarena_scores, enrich_with_lmarena
from components.open_router.or_model_filtering import get_models

# Which components/lmarena/lmarena_download.py --subset CSV to blend in (run that script,
# from this folder, to (re)generate it).
LMARENA_SUBSET = 'vision'


def load_and_sort_models():
    """Load image-capable models from OpenRouter and sort them by LM Arena vision score."""
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

        if df_models.empty:
            st.error("No image-capable models found. Please check your internet connection or OpenRouter API.")
            return

        score_df = load_lmarena_scores(LMARENA_SUBSET)
        if score_df.empty:
            st.warning("Could not load LM Arena scores. Models are not sorted by capability.")

        df_models = enrich_with_lmarena(df_models, score_df)
        st.session_state.matched_models_count = int(df_models['lm_arena_score'].notna().sum())

        df_models = df_models.sort_values('lm_arena_score', ascending=False, na_position='last', kind='stable')
        df_models['lm_arena_score'] = df_models['lm_arena_score'].where(df_models['lm_arena_score'].notna(), 'N/A')

        models = df_models.to_dict('records')
        st.session_state.all_models_data = models
        st.session_state.total_image_capable_models = len(models)
        set_default_model(models)


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
