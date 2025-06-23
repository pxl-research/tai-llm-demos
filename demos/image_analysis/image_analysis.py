import streamlit as st

from app_config import OPENROUTER_API_KEY, SESSION_KEYS
from model_manager import (
    load_and_sort_models,
    prepare_api_messages,
    call_model_api
)
from ui_components import (
    initialize_session_state,
    setup_model_selector,
    display_chat_history,
    handle_image_upload,
    add_clear_chat_button
)

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="OpenRouter Image Analysis", layout="centered")
st.title("OpenRouter Image Analysis Demo")

# --- Initialize Session State ---
initialize_session_state(SESSION_KEYS)


# --- Main Application Flow ---
def main():
    """Main application flow"""
    # Load models
    load_and_sort_models()

    # Setup sidebar model selector
    setup_model_selector()

    # Add clear chat button to sidebar
    add_clear_chat_button()

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
