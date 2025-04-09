# LLM Chat

## What's in this folder?

This folder contains some basic **chatbot** examples:

- `chat_oai.py`: A basic chat app using the Azure OpenAI `chat.completions.create` API. This example also includes token and cost estimation.

- `chat_or_with_logs.py`: A similar app using OpenRouter, that also stores logs of the conversation in the `logs/` directory.

## Configuration

To install the necessary libraries, use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `env.example` file and enter your personal **keys** and **endpoints** therein. The `chat_oai.py` script requires Azure OpenAI credentials, while `chat_or_with_logs.py` requires OpenRouter credentials.

## Use

Run the Python script from the terminal (or your IDE). For example: `python chat_oai.py` or `python chat_or_with_logs.py`.

_For more info regarding how Gradio works, please refer to the general README in this repository._

## Notes

The `chat_oai.py` script provides token and cost estimations, which are printed to the console.

## Screenshots

### chat_oai.py
`./demos/basic_chat`

![gradio-chat.png](../../assets/screenshots/gradio-chat.png)
