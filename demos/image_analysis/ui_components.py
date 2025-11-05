from typing import Dict, List, Any

import streamlit as st

from utils import encode_image_to_base64
from app_config import (
    PROMPT_PRICE_THRESHOLD,
    COMPLETION_PRICE_THRESHOLD,
    IMAGE_PRICE_THRESHOLD
)
from model_manager import update_selected_model

def initialize_session_state(session_keys: Dict[str, Any]):
    """Initialize all required session state variables"""
    for var, default in session_keys.items():
        if var not in st.session_state:
            st.session_state[var] = default


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


def setup_model_selector():
    """Display model selection UI in the sidebar"""
    model_ids = [model['id'] for model in st.session_state.all_models_data]
    
    if not model_ids:
        st.sidebar.warning("No models available.")
        return
        
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
            f"No models matched with scores from CSV (out of "
            f"{st.session_state.total_image_capable_models} total image-capable models)."
        )


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "image":
                st.image(message["content"], caption="Uploaded Image", use_container_width=True)


def handle_image_upload():
    """Process an uploaded image file"""
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"image_uploader_{st.session_state.file_uploader_key_counter}"
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

def clear_chat_history():
    """Clears the chat history and resets image-related session state."""
    st.session_state.messages = []
    st.session_state.current_image_message = None
    st.session_state.last_uploaded_file_id = None
    st.session_state.file_uploader_key_counter += 1 # Increment to reset file uploader

def add_clear_chat_button():
    """Adds a button to clear the chat history."""
    st.sidebar.button("Clear Chat", on_click=clear_chat_history)
