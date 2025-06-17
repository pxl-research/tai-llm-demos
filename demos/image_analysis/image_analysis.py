import os
from typing import Dict, List, Any

import streamlit as st
from dotenv import load_dotenv

from utils import (
    get_image_capable_models,
    encode_image_to_base64,
    call_openrouter_api,
    load_model_scores,
    sort_models_by_score
)

# --- Configuration ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = 'google/gemini-2.0-flash-001'

# Price thresholds for highlighting expensive models (per million tokens)
PROMPT_PRICE_THRESHOLD = 1.5
COMPLETION_PRICE_THRESHOLD = 7.5
IMAGE_PRICE_THRESHOLD = 7.5

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="OpenRouter Image Analysis", layout="centered")
st.title("OpenRouter Image Analysis Demo")


# --- Initialize Session State ---
def initialize_session_state():
    """Initialize all required session state variables"""
    session_vars = {
        "messages": [],
        "image_capable_models": [],
        "selected_model_id": None,
        "model_scores": {},
        "matched_models_count": 0,
        "last_uploaded_file_id": None,
        "all_models_data": [],
        "total_image_capable_models": 0,
    }

    for var, default in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default


initialize_session_state()


# --- Model Loading and Selection Logic ---
def load_and_sort_models():
    """Load models from OpenRouter API and sort them by score"""
    # Only load models if not already loaded
    if not st.session_state.all_models_data:
        # Get models that support image processing
        models = get_image_capable_models()
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


def set_default_model(models):
    """Set the default model from available options"""
    # Try to use the preferred default model if available
    if any(model['id'] == DEFAULT_MODEL for model in models):
        st.session_state.selected_model_id = DEFAULT_MODEL
    # Otherwise use the first available model
    elif models:
        st.session_state.selected_model_id = models[0]['id']


def update_selected_model():
    """Callback when user selects a different model"""
    st.session_state.selected_model_id = st.session_state.model_selector


# Load and prepare the models
load_and_sort_models()

# Display model selection dropdown
model_ids = [model['id'] for model in st.session_state.all_models_data]


def display_model_details(model: Dict[str, Any]):
    """Display details about the selected model in the sidebar"""
    st.sidebar.markdown(f"### **{model['id']}**")

    # Extract model details
    pricing = model.get('pricing', {})
    prompt_price = float(pricing.get('prompt', 0)) * 1000000
    completion_price = float(pricing.get('completion', 0)) * 1000000
    image_price_raw = pricing.get('image')
    lm_arena_score = model.get('lm_arena_score', 'N/A')
    top_provider = model.get('top_provider', {})
    max_completion_tokens = top_provider.get('max_completion_tokens', 'N/A')

    # Show score
    st.sidebar.markdown(f"**LM Arena Score:** {lm_arena_score}")

    # Format and display image price
    if image_price_raw is not None and float(image_price_raw) != 0:
        image_price_per_10k = float(image_price_raw) * 10000
        image_price_str = f"${image_price_per_10k:.2f} / 10K tokens"
        if image_price_per_10k > IMAGE_PRICE_THRESHOLD:
            image_price_str = f"<span style='color: orange;'>{image_price_str}</span>"
        st.sidebar.markdown(f"**Image Price:** {image_price_str}", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"**Image Price:** N/A")

    # Format and display prompt price
    prompt_price_str = f"${prompt_price:.2f} / M tokens"
    if prompt_price > PROMPT_PRICE_THRESHOLD:
        prompt_price_str = f"<span style='color: orange;'>{prompt_price_str}</span>"
    st.sidebar.markdown(f"**Prompt Price:** {prompt_price_str}", unsafe_allow_html=True)

    # Format and display completion price
    completion_price_str = f"${completion_price:.2f} / M tokens"
    if completion_price > COMPLETION_PRICE_THRESHOLD:
        completion_price_str = f"<span style='color: orange;'>{completion_price_str}</span>"
    st.sidebar.markdown(f"**Completion Price:** {completion_price_str}", unsafe_allow_html=True)

    # Show additional model details
    st.sidebar.markdown(f"**Context Length:** {model.get('context_length', 'N/A')} tokens")
    st.sidebar.markdown(f"**Max Completion Tokens:** {max_completion_tokens}")
    st.sidebar.markdown(f"**Provider:** {model['id'].split('/')[0]}")


if model_ids:
    st.sidebar.header("Model Settings")

    # Set the current selection index
    current_index = 0
    if st.session_state.selected_model_id in model_ids:
        current_index = model_ids.index(st.session_state.selected_model_id)

    st.sidebar.selectbox(
        "Select a model:",
        model_ids,
        index=current_index,
        key="model_selector",
        on_change=update_selected_model
    )

    # Get the selected model data
    selected_model = next(
        (model for model in st.session_state.all_models_data
         if model['id'] == st.session_state.selected_model_id),
        None
    )

    # Display model details in sidebar
    if selected_model:
        display_model_details(selected_model)

    # Show match statistics
    if st.session_state.matched_models_count > 0:
        st.sidebar.info(
            f"Matched {st.session_state.matched_models_count} out of "
            f"{st.session_state.total_image_capable_models} models with scores from CSV."
        )
    else:
        st.sidebar.warning(
            f"No models matched with scores from CSV (out of "                f"{st.session_state.total_image_capable_models} total image-capable models)."
        )
else:
    st.sidebar.warning("No models available.")


# --- Chat UI Functions ---
def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "image":
                st.image(message["content"], caption="Uploaded Image", use_column_width=True)


def handle_image_upload():
    """Process an uploaded image file"""
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_uploader"
    )

    if uploaded_file is not None:
        # Only process the file if it's new
        if uploaded_file.file_id != st.session_state.last_uploaded_file_id:
            # Add to chat history
            st.session_state.messages.append({
                "role": "user",
                "type": "image",
                "content": uploaded_file
            })

            # Encode for API
            image_data_url = encode_image_to_base64(uploaded_file)

            # Store for API request
            st.session_state.current_image_message = {
                "type": "image_url",
                "image_url": {"url": image_data_url}
            }

            # Update tracking
            st.session_state.last_uploaded_file_id = uploaded_file.file_id

            # Refresh display
            st.rerun()


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


# --- Main Application Flow ---
def main():
    """Main application flow"""
    # Display existing chat messages
    display_chat_history()

    # Handle image upload
    handle_image_upload()

    # Process chat input
    if prompt := st.chat_input("Ask about the image or type your message..."):
        # Verify requirements
        if not OPENROUTER_API_KEY:
            st.error("OpenRouter API Key not found. Please set it in your .env file.")
            st.stop()

        if not st.session_state.selected_model_id:
            st.error("No model selected. Please select a model from the sidebar.")
            st.stop()

        # Add to chat history
        st.session_state.messages.append({
            "role": "user",
            "type": "text",
            "content": prompt
        })

        # Prepare API messages
        api_messages = prepare_api_messages(prompt)

        # Call model API
        call_model_api(api_messages)


# Run the application
if __name__ == "__main__":
    main()
