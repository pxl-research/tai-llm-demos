# TransformAI LLM Chat

## What's in this repository?

This repository contains chatbot and related examples using Azure OpenAI and OpenRouter as the LLM providers.

- `demos/basic_chat` contains basic chat apps using the Azure OpenAI Chat API (with token/cost estimation) and OpenRouter.

- `demos/rag` demonstrates the document retrieval part of a RAG system, using ChromaDB for vector storage and markitdown for document parsing.

- `demos/tool_calling` showcases tool calling with OpenRouter, including tools for document retrieval, web search, and file I/O.

- `demos/model_choice` allows chatting with different models via the OpenRouter API.

- `demos/slack_bot` provides demo code for a Slack bot with LLM integration using Azure OpenAI and OpenRouter.

- `demos/voice_notes` provides a tool to transcribe and summarize voice notes using OpenRouter.

- `applications/chat_with_rag` is a chat application using the Azure OpenAI "Assistants API" with RAG and a custom, bcrypt-based authentication method.

- `applications/faq_tool` is a chatbot that answers questions based on uploaded documents (PDF, DOCX, PPTX, XLSX, XLS). It uses OpenRouter for the LLM and RAG for document retrieval.

- `gui` is a proof-of-concept local GUI-based LLM chat app using wxPython (WARNING: this is a work in progress).

## Configuration

To install the necessary libraries, use `pip install -r requirements.txt`

Note: to minimize the number of libraries installed, each demo folder has its own `requirements.txt` file with specific dependencies.

Please create an `.env` file with the same structure as the provided `.env.example` files (found in each demo folder), and enter your personal API keys and endpoints therein.

## Use

Run the Python script from the terminal (or your IDE).

For more detailed information, open the README files in the respective demo folders.

### Gradio

For [Gradio](https://www.gradio.app/guides/creating-a-chatbot-fast) projects, this will print a **URL** to the console. Surf to the generated address in your browser to use the Gradio web UI.

The default URL is http://127.0.0.1:7860, which runs locally. If the address is specified to `0.0.0.0`, it will also be available to other computers on your network, using your IP address. To create a publicly accessible link, set `share=True` in the Gradio `launch()` call.

## Screenshots

### launch_ui.py

`applications/chat_with_rag`

![gradio-logviewer.png](assets/screenshots/gradio-logviewer.png)

## License

Icons by <a target="_blank" href="https://icons8.com">Icons8</a>

## Feedback

Feedback and bug reports are welcome, please [email us](mailto:servaas.tilkin@pxl.be) or submit a feature request.
