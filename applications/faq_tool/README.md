# FAQ Tool

## What's in this folder?

This folder contains a simple FAQ tool that uses a language model to answer questions based on a collection of documents.

It consists of two main parts:

*   **Document Upload UI:** Allows you to upload and manage the documents used to answer questions.
*   **FAQ Chat Interface:** Provides a chat interface where you can ask questions and receive answers based on the uploaded documents.

## Contents

*   `launch_faq_tool.py`: Launches the FAQ chat interface.
*   `launch_upload_ui.py`: Launches the document upload UI.
*   `tools_rag.py`: Contains the logic for querying the document store.
*   `requirements.txt`: Lists the required Python libraries.
*   `.env`: Stores configuration variables such as API keys and file paths.
*   `.env.example`: An example .env file

## Configuration

1.  Install the necessary libraries using `pip install -r requirements.txt`.
2.  Create a `.env` file with the same structure as the provided `.env.example` file.

## Use

1.  **Upload Documents:**
    *   Run `launch_upload_ui.py` to start the document upload UI. This will launch a Gradio interface.
    *   Before running, change the default username and password in the `launch_upload_ui.py` file.
    *   Log in using the username and password you set in `launch_upload_ui.py`.
    *   Upload documents (PDF, DOCX, PPTX, XLSX, XLS) to the interface. These documents will be processed and stored in the document store.
2.  **Chat with the FAQ Tool:**
    *   Run `launch_faq_tool.py` to start the FAQ chat interface. This will launch a Gradio interface.
    *   Ask questions related to the content of the uploaded documents. The tool will use the language model to find relevant information and provide an answer.

## Notes

*   The tool uses OpenRouter to access a language model. You will need an OpenRouter API key to use this tool.
*   The document store is persisted to disk using ChromaDB.
*   The `tools_rag.py` file contains the logic for querying the document store.
*   Log files are stored in the `logs` folder.