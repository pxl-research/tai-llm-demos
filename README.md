---
title: TransformAI LLM Chat
emoji: 💬
colorFrom: blue
colorTo: red
sdk: gradio
app_file: gradio-blocks/launch-ui.py
pinned: true
---

# TransformAI LLM Chat

## What's in this repository?
This repository contains two "chatbot" examples using the Azure OpenAI as LLM under the hood:
- `gradio-chat` a basic chat app using the "Completions API"
- `gradio-blocks` a chat app using the "Assistant API", including a chat history viewer

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

### chat.py
`/gradio-chat`

![gradio-chat.png](assets/screenshots/gradio-chat.png)

### blocks.py
`/gradio-blocks`

![gradio-blocks.png](assets/screenshots/gradio-blocks.png)

### logviewer.py
`/gradio-blocks`

![gradio-logviewer.png](assets/screenshots/gradio-logviewer.png)

### License
Icons by <a target="_blank" href="https://icons8.com">Icons8</a>
