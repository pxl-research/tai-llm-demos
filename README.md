# TransformAI LLM Chat

## What's in this repository?
This repository contains two "chatbot" examples using the Azure OpenAI as LLM under the hood:
- `gradio-chat` a basic chat app with "Completions API"
- `gradio-blocks` a better chat app with "Assistant API"

## Configuration
To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file, 
and enter your personal **key** and **endpoint** therein.

## Use
Run the python script from the terminal (or your IDE). 

It will print out an **URL** to the console. 
The default URL is http://127.0.0.1:7860, which is running local only. 
To create a public link, set `share=True` in the Gradio `launch()` call.

Surf to the generated address in your browser to use the (Gradio) web UI

## Screenshots

### gradio-chat
![gradio-chat.png](assets/screenshots/gradio-chat.png)

### gradio-blocks
![gradio-blocks.png](assets/screenshots/gradio-blocks.png)
