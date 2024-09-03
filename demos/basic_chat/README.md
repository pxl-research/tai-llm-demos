# TransformAI LLM Chat

## What's in this folder?
This folder contains some basic **chatbot** examples:

- `demos/basic_chat` a basic chat app using the OpenAI "Completions API"

- `demos/chat_or_with_logs` a very similar app using OpenRouter, that also stores logs of the conversation


## Configuration
To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file, 
and enter your personal **keys** and **endpoints** therein.

## Use
Run the python script from the terminal (or your IDE). 

It will print out a **URL** to the console. 
The default URL for [Gradio](https://www.gradio.app/guides/creating-a-chatbot-fast) is http://127.0.0.1:7860, which runs local only. 

If the address is specified to `0.0.0.0`, 
it will also be available to other computers in your network, using your IP address.

To create a publicly accessible link, set `share=True` in the Gradio `launch()` call.

Surf to the generated address in your browser to use the Gradio web UI.

## Screenshots

### chat.py
`./demos/basic_chat`

![gradio-chat.png](../../assets/screenshots/gradio-chat.png)
