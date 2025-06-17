# Development Plan for Streamlit Image Analysis Demo

This plan outlines the steps to create a Streamlit application that leverages OpenRouter's API for multimodal (text and image) interactions.

## Phase 1: Setup and Core Functionality

This phase focuses on setting up the project structure and implementing the essential logic for interacting with the OpenRouter API and handling images.

1.  **Project Structure:**

    - Create `app.py` in `demos/image_analysis/` (this will be our main Streamlit application).
    - Create `requirements.txt` in the same directory (to list necessary Python packages like `streamlit`, `requests`, `python-dotenv`).
    - Create `.env.example` for users to configure their `OPENROUTER_API_KEY`.
    - Create `utils.py` in `demos/image_analysis/` to house reusable helper functions.

2.  **API Key Management:**

    - Implement logic in `app.py` to load the `OPENROUTER_API_KEY` from a `.env` file using `python-dotenv`.

3.  **Image-Capable Model Discovery (`utils.py`):**

    - Develop a function `get_image_capable_models()` that:
      - Fetches all models from the OpenRouter API (`https://openrouter.ai/api/v1/models`).
      - Filters this list to identify models that explicitly support both "text" and "image" in their `input_modalities`.
      - Returns a list of the IDs of these suitable models.
    - Initially, the app will use the first model from this list or a sensible default.

4.  **Image Encoding Utility (`utils.py`):**

    - Create a function `encode_image_to_base64(image_file)` that accepts a file-like object (from Streamlit's file uploader).
    - This function will read the image, base64-encode it, and format it as a data URL string (e.g., `data:image/jpeg;base64,...`) as required by OpenRouter.

5.  **OpenRouter API Interaction (`utils.py`):**
    - Develop a function `call_openrouter_api(model_id, messages, api_key)` that:
      - Constructs the JSON payload for the `/api/v1/chat/completions` endpoint, including the `model_id` and the `messages` array (which will contain both text and image parts).
      - Sends a POST request to the OpenRouter API with the `Authorization` header set using the provided `api_key`.
      - Parses the API response and returns the generated content from the model.

## Phase 2: Streamlit User Interface Development

This phase focuses on building the interactive Streamlit application.

1.  **Basic Streamlit App Structure (`app.py`):**

    - Set up the main Streamlit page layout and title.
    - Initialize the chat history in `st.session_state` to maintain conversation context across reruns.

2.  **Chat Interface:**

    - Iterate through the `st.session_state` chat history to display messages.
    - Use `st.chat_message` to differentiate between user and model messages.
    - Render message content using `st.markdown` to support rich text formatting.
    - Implement `st.chat_input` at the bottom for users to type their text prompts.

3.  **Image Upload Functionality:**

    - Integrate `st.file_uploader` to allow users to upload image files (e.g., PNG, JPEG, WebP).
    - When an image is uploaded:
      - Display the uploaded image within the chat interface.
      - Call `encode_image_to_base64` from `utils.py` to prepare the image for the API call.
      - Add the image content (as a `{"type": "image_url", "image_url": {"url": "..."}}` object) to the `messages` array.

4.  **Combined Input Handling:**
    - When a user submits a text prompt or uploads an image, construct the `messages` array for the OpenRouter API call. This array will contain a mix of `{"type": "text", "text": "..."}` and `{"type": "image_url", "image_url": {"url": "..."}}` objects, maintaining the conversation flow.
    - Call `call_openrouter_api` with the constructed messages.
    - Append the model's response to the chat history.

## Phase 3: Advanced Features (Secondary Priority)

This phase addresses the model selection and filtering.

1.  **Model Selection UI:**
    - Add a sidebar (`st.sidebar`) or an expandable section (`st.expander`) for model settings.
    - Populate a `st.selectbox` with the names of the image-capable models obtained from `get_image_capable_models()`.
    - Allow the user to select their preferred model, which will then be used for subsequent API calls.
    - (Optional, if complexity allows): Implement basic filtering/sorting options for the model list if it becomes extensive.
