# TransformAI LLM Chat

## What's in this repository?

This repository contains some "chatbot" and related examples using [OpenRouter](https://openrouter.ai/)
and [Azure OpenAI](https://oai.azure.com/) as the LLM's under the hood:

- `demos/basic_chat` a basic chat app using the OpenAI Completions API and a similar example with OpenRouter

- `demos/rag` tools and utilities to showcase RAG using ChromaDB

- `demos/slack_bot` demo code for a Slack bot with LLM integration

- `chat_with_rag` a more fleshed out chat app using the OpenAI "Assistant API", including RAG and a chat history viewer

- `class_based` the stub for refactoring these demos into more modular, reusable code (work in progress)

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file,
and enter your personal (OpenRouter or Azure OpenAI) **key** and **endpoint** therein.

## Use

Run the python script from the terminal (or your IDE).

For more detailed instructions, open the README files in the respective folders

## Screenshots

### launch_ui.py

`./chat_with_rag`

![gradio-logviewer.png](assets/screenshots/gradio-logviewer.png)

## License

Icons by <a target="_blank" href="https://icons8.com">Icons8</a>
