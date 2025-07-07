blocks_llm_chat_with_rag.py: This file contains the main logic for a chat application using Azure OpenAI and RAG. It sets up an assistant with instructions and tools, handles user input, interacts with the OpenAI API, and manages chat history. It also includes functionality for estimating token counts and storing thread logs.

blocks_rag_upload.py: This file handles file uploads and manages a Chroma document store for RAG. It allows users to upload files, add them to the Chroma database, list existing collections (documents), and remove collections.

blocks_view_history.py: This file provides functionality for viewing chat history from log files. It allows users to select a log file, load its content, and display the chat history in a structured format. It also includes functions for setting the log folder and removing log files.

fn_rag.py: This file defines functions for interacting with the Chroma document store. It includes functions to list available documents and perform lookups in the documentation based on a given query.

launch_ui.py: This file is the main file for launching the Gradio UI of the chat application. It defines the layout of the UI, including the chatbot, file upload section, and history viewer. It also defines the event handlers for user interactions, such as sending prompts, clearing the chat, uploading files, and selecting log files. It uses `fn_auth.auth_method` for authentication.
