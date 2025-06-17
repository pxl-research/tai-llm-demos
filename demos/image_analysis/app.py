import os

import streamlit as st
from dotenv import load_dotenv

from utils import get_image_capable_models, encode_image_to_base64, call_openrouter_api, load_model_scores, \
    sort_models_by_score

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = 'google/gemini-2.0-flash-001'

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="OpenRouter Image Analysis", layout="centered")
st.title("OpenRouter Image Analysis Demo")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "image_capable_models" not in st.session_state:
    st.session_state.image_capable_models = []
if "selected_model_id" not in st.session_state:
    st.session_state.selected_model_id = None
if "model_scores" not in st.session_state:
    st.session_state.model_scores = {}
if "matched_models_count" not in st.session_state:
    st.session_state.matched_models_count = 0
if "last_uploaded_file_id" not in st.session_state:
    st.session_state.last_uploaded_file_id = None
if "all_models_data" not in st.session_state:
    st.session_state.all_models_data = [] # Stores full model objects

# --- Model Selection and Sorting ---
if not st.session_state.all_models_data:
    st.session_state.all_models_data = get_image_capable_models() # Now returns full model objects
    st.session_state.total_image_capable_models = len(st.session_state.all_models_data) # Store total count
    
    # Load model scores from CSV
    st.session_state.model_scores = load_model_scores()
    
    if st.session_state.all_models_data and st.session_state.model_scores:
        # Sort models by score
        sorted_models_data, matched_count = sort_models_by_score(
            st.session_state.all_models_data,
            st.session_state.model_scores
        )
        st.session_state.all_models_data = sorted_models_data
        st.session_state.matched_models_count = matched_count
        
        # Set default model: prioritize DEFAULT_MODEL if available, else use the top-ranked
        if any(model['id'] == DEFAULT_MODEL for model in st.session_state.all_models_data):
            st.session_state.selected_model_id = DEFAULT_MODEL
        else:
            st.session_state.selected_model_id = st.session_state.all_models_data[0]['id']

    elif st.session_state.all_models_data:
        # If no scores loaded, still try to set DEFAULT_MODEL if available, else use first
        if any(model['id'] == DEFAULT_MODEL for model in st.session_state.all_models_data):
            st.session_state.selected_model_id = DEFAULT_MODEL
        else:
            st.session_state.selected_model_id = st.session_state.all_models_data[0]['id']
        st.warning("Could not load model scores. Models are not sorted by capability.")
    else:
        st.error("No image-capable models found. Please check your internet connection or OpenRouter API.")

# Get list of model IDs for the selectbox
model_ids_for_selectbox = [model['id'] for model in st.session_state.all_models_data]

if model_ids_for_selectbox:
    st.sidebar.header("Model Settings")
    st.session_state.selected_model_id = st.sidebar.selectbox(
        "Select a model:",
        model_ids_for_selectbox,
        index=model_ids_for_selectbox.index(st.session_state.selected_model_id) if st.session_state.selected_model_id in model_ids_for_selectbox else 0
    )
    
    # Find the full model object for the selected model ID
    selected_model_data = next((model for model in st.session_state.all_models_data if model['id'] == st.session_state.selected_model_id), None)

    if selected_model_data:
        st.sidebar.markdown(f"### **{selected_model_data['id']}**")
        st.sidebar.markdown(f"**Provider:** {selected_model_data['id'].split('/')[0]}")
        
        pricing = selected_model_data.get('pricing', {})
        prompt_price = float(pricing.get('prompt', 0)) * 1000000
        completion_price = float(pricing.get('completion', 0)) * 1000000
        
        st.sidebar.markdown(f"**Prompt Price:** ${prompt_price:.2f} / M tokens")
        st.sidebar.markdown(f"**Completion Price:** ${completion_price:.2f} / M tokens")
        st.sidebar.markdown(f"**Context Length:** {selected_model_data.get('context_length', 'N/A')} tokens")
        
        top_provider = selected_model_data.get('top_provider', {})
        max_completion_tokens = top_provider.get('max_completion_tokens', 'N/A')
        st.sidebar.markdown(f"**Max Completion Tokens:** {max_completion_tokens}")

    if st.session_state.matched_models_count > 0:
        st.sidebar.info(f"Matched {st.session_state.matched_models_count} out of {st.session_state.total_image_capable_models} models with scores from CSV.")
    else:
        st.sidebar.warning(f"No models matched with scores from CSV (out of {st.session_state.total_image_capable_models} total image-capable models).")
else:
    st.sidebar.warning("No models available.")

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"], caption="Uploaded Image", use_column_width=True)

# --- Image Upload ---
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"], key="image_uploader")

if uploaded_file is not None:
    # Check if this file has already been processed in the current session state
    if uploaded_file.file_id != st.session_state.last_uploaded_file_id:
        # Display uploaded image in chat
        st.session_state.messages.append({"role": "user", "type": "image", "content": uploaded_file})
        
        # Encode image for API call
        base64_image_data_url = encode_image_to_base64(uploaded_file)
        
        # Prepare message content for API
        image_message_content = {
            "type": "image_url",
            "image_url": {"url": base64_image_data_url}
        }
        
        # Add image message to current API request messages
        st.session_state.current_image_message = image_message_content
        
        # Update the last processed file ID
        st.session_state.last_uploaded_file_id = uploaded_file.file_id
        
        st.rerun() # Rerun to display the image immediately and process next steps

# --- Chat Input ---
if prompt := st.chat_input("Ask about the image or type your message..."):
    if not OPENROUTER_API_KEY:
        st.error("OpenRouter API Key not found. Please set it in your .env file.")
        st.stop()

    if not st.session_state.selected_model_id:
        st.error("No model selected. Please select a model from the sidebar.")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})

    # Prepare messages for API call
    api_messages = []
    # Add previous messages from history
    for msg in st.session_state.messages:
        if msg["type"] == "text":
            api_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})
        elif msg["type"] == "image" and msg["role"] == "user":
            # Re-encode image if it's from history (Streamlit re-runs might lose file object)
            # For simplicity, we'll assume images are only sent once per turn for now
            # A more robust solution would store base64 or handle re-upload
            # For now, we'll only include the *current* uploaded image if any
            pass # Handled by current_image_message

    # Add current user prompt
    current_user_content = [{"type": "text", "text": prompt}]
    
    # Add current uploaded image if available
    if "current_image_message" in st.session_state and st.session_state.current_image_message:
        current_user_content.insert(0, st.session_state.current_image_message) # Prepend image to content
        del st.session_state.current_image_message # Clear after use

    api_messages.append({"role": "user", "content": current_user_content})

    # Call OpenRouter API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_json = call_openrouter_api(
                st.session_state.selected_model_id,
                api_messages,
                OPENROUTER_API_KEY
            )
            if response_json and response_json.get("choices"):
                assistant_response = response_json["choices"][0]["message"]["content"]
                st.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": assistant_response})
            else:
                st.error("Failed to get a response from the model.")
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": "Error: Could not get a response."})
