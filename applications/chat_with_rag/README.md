# Chat with RAG Application

## Project Overview

This application demonstrates a chat interface that leverages Retrieval-Augmented Generation (RAG) with Azure OpenAI and ChromaDB to provide intelligent responses based on uploaded documents. Users can upload documents, chat with the application, and view chat history. The application uses Azure OpenAI for the language model and requires a valid API key and endpoint. User authentication is handled by a custom method that relies on bcrypt-hashed passwords. The document store is persisted to disk using ChromaDB, and chat logs are stored in the `logs` folder. The application uses a thread to manage the chat history.

## Technologies Used

- Python
- Gradio
- Azure OpenAI
- ChromaDB
- dotenv
- tiktoken

## Contents

- `blocks_llm_chat_with_rag.py`: This file contains the main logic for a chat application using Azure OpenAI and RAG. It sets up an assistant with instructions and tools, handles user input, interacts with the OpenAI API, and manages chat history. It also includes functionality for estimating token counts and storing thread logs.
- `blocks_rag_upload.py`: This file handles file uploads and manages a Chroma document store for RAG. It allows users to upload files, add them to the Chroma database, list existing collections (documents), and remove collections.
- `blocks_view_history.py`: This file provides functionality for viewing chat history from log files. It allows users to select a log file, load its content, and display the chat history in a structured format. It also includes functions for setting the log folder and removing log files.
- `fn_rag.py`: This file defines functions for interacting with the Chroma document store. It includes functions to list available documents and perform lookups in the documentation based on a given query.
- `launch_ui.py`: This file is the main file for launching the Gradio UI of the chat application. It defines the layout of the UI, including the chatbot, file upload section, and history viewer. It also defines the event handlers for user interactions, such as sending prompts, clearing the chat, uploading files, and selecting log files. It uses `fn_auth.auth_method` for authentication.
- `.env.example`: An example .env file
- `.passwd`: Stores user authentication credentials.

## Configuration

The project dependencies are listed in `requirements.txt`.

1.  Install dependencies: `pip install -r requirements.txt`
2.  Configure the application: Create a `.env` file based on the provided `.env.example`. This file requires you to set the following environment variables:
    - `AOA_API_KEY`: Your Azure OpenAI API key.
    - `AOA_ENDPOINT`: Your Azure OpenAI endpoint.
    - `CHROMA_LOCATION`: The location of the ChromaDB store.
      Also, set up user authentication by following the instructions in `demos/components/fn_auth.py` and configuring the `.passwd` file.

## Use

1.  Run `launch_ui.py` to start the application. This will launch a Gradio interface.
2.  Log in using the credentials configured in the `.passwd` file.
3.  Upload documents using the "Upload" tab.
4.  Chat with the application using the "Chat" tab.
5.  View chat history using the "History" tab.

## Notes

- This application uses Azure OpenAI for the language model and requires a valid API key and endpoint.
- User authentication is handled by a custom method (defined in `demos/components/fn_auth.py`) that relies on bcrypt-hashed passwords.
- The document store is persisted to disk using ChromaDB (data is stored in the `../../demos/rag/store/` directory).
- Chat logs are stored in the `logs` folder.
- The application uses a thread to manage the chat history.
