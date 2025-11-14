# TransformAI LLM Chat

## What's in this repository?

This repository contains chatbot and related examples using Azure OpenAI and OpenRouter as the LLM providers.

### Demos

- [Basic Chat](demos/basic_chat/README.md): Basic chatbot examples using Azure OpenAI and OpenRouter, with token and cost estimation.
- [Image Analysis](demos/image_analysis/README.md): A Streamlit app for multimodal image and text analysis using OpenRouter.
- [MCP Server for File I/O](demos/mcp_server_file_io/README.md): An MCP server for interacting with the file system.
- [Model Choice](demos/model_choice/README.md): A chatbot demo allowing users to choose which LLM to interact with.
- [RAG Demo](demos/rag/README.md): Demonstrates document retrieval using ChromaDB and markitdown.
- [Slack Chatbot](demos/slack_bot/README.md): Slack bot examples with tool-calling capabilities.
- [Tool Calling](demos/tool_calling/README.md): A chatbot using OpenRouter with tool-calling functionality.
- [Voice Notes](demos/voice_notes/README.md): A Gradio tool for transcribing and summarizing audio files.

### Applications

- [Chat with RAG](applications/chat_with_rag/README.md): A chat application using Azure OpenAI "Assistants API" with RAG and a custom authentication method.
- [FAQ Tool](applications/faq_tool/README.md): A chatbot that answers questions based on uploaded documents (PDF, DOCX, PPTX, XLSX, XLS).

## Configuration

To install the necessary libraries, use `pip install -r requirements.txt`

Note: To minimize the number of libraries installed, each demo folder has its own `requirements.txt` file with specific dependencies.

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
