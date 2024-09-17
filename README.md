# TransformAI LLM Chat

## What's in this repository?

This repository contains some "chatbot" and related examples using [OpenRouter](https://openrouter.ai/)
and [Azure OpenAI](https://oai.azure.com/) as the LLM providers under the hood.

- `demos/basic_chat` contains a basic chat app using the OpenAI Completions API and a similar example with OpenRouter

- `demos/rag` has some tools and utilities to showcase RAG retrieval

- `demos/tool_calling` is a basic demo that links an LLM with some local methods (including document retrieval)

- `demos/slack_bot` consists of demo code for a Slack bot with LLM integration

- `chat_with_rag` is a more fleshed out chat app using the OpenAI "Assistants API",
and includes RAG and a chat history viewer

- `gui` a proof-of-concept of a local GUI based llm-chat app using [wxPython](https://wxpython.org/index.html) 
(WARNING: this is a work in progress)

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Note: to minimize the amount of libraries installed,
we have provided smaller (more specific) requirements files in the demo folders themselves.

Please create an `.env` file with the same structure as the provided `.env.example` files,
and enter your personal (OpenRouter or Azure OpenAI) **key** and **endpoint** therein.

## Use

Run the Python script from the terminal (or your IDE).

For more detailed information, open the README files in the respective demo folders

### Gradio

For [Gradio](https://www.gradio.app/guides/creating-a-chatbot-fast) projects this will print a **URL** to the console.
Surf to the generated address in your browser to use the Gradio web UI.

The default URL is http://127.0.0.1:7860, which runs local only.
If the address is specified to `0.0.0.0`,
it will also be available to other computers in your network, using your IP address.
To create a publicly accessible link, set `share=True` in the Gradio `launch()` call.

## Screenshots

### launch_ui.py

`./chat_with_rag`

![gradio-logviewer.png](assets/screenshots/gradio-logviewer.png)

## License

Icons by <a target="_blank" href="https://icons8.com">Icons8</a>

## Feedback

Feedback and bug reports are welcome, 
please [email us](mailto:servaas.tilkin@pxl.be) or submit a feature request. 
