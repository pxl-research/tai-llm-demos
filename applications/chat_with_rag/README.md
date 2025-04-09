# Chat with RAG Application

## What's in this folder?

This folder contains a chat application that uses Retrieval-Augmented Generation (RAG) with Azure OpenAI and ChromaDB.

## Contents

*   `blocks_llm_chat_with_rag.py`: Implements the chat interface.
*   `blocks_rag_upload.py`: Implements document upload and management.
*   `blocks_view_history.py`: Implements chat history viewing.
*   `fn_rag.py`: Contains functions for querying the document store.
*   `launch_ui.py`: Launches the main Gradio interface.
*   `.env.example`: An example .env file
*   `.passwd`: Stores user authentication credentials.

## Configuration

1.  Install dependencies: `pip install -r requirements.txt`
2.  Configure the application: Create a `.env` file based on the provided `.env.example`, and set up user authentication by following the instructions in `demos/components/fn_auth.py` and configuring the `.passwd` file.

## Use

1.  Run `launch_ui.py` to start the application. This will launch a Gradio interface.
2.  Log in using the credentials configured in the `.passwd` file.
3.  Upload documents using the "Upload" tab.
4.  Chat with the application using the "Chat" tab.
5.  View chat history using the "History" tab.

## Notes

*   This application uses Azure OpenAI for the language model and requires a valid API key and endpoint.
*   User authentication is handled by a custom method (defined in `demos/components/fn_auth.py`) that relies on bcrypt-hashed passwords.
*   The document store is persisted to disk using ChromaDB (data is stored in the `../../demos/rag/store/` directory).
*   Chat logs are stored in the `logs` folder.
*   The application uses a thread to manage the chat history.