# Voice Note Summary Demo
TransformAI

## What's in this folder?
This folder contains a basic **voice note summary** example:

- `voice_notes/summarizer.py` the Gradio tool (website)

- `voice_notes/llm_functions.py` the LLM summary prompt and methods (using OpenRouter)


## Configuration
To install the necessary libraries use `pip install -r requirements.txt`

**WARNING**: these libraries are quite big and take a while to install

If you do not have an NVIDIA graphics card, 
the transcription will be performed on the CPU and may take relatively long.

Please create an `.env` file with the same structure as the provided `.env.example` file, 
and enter your personal OpenRouter **keys** and **endpoints** therein.

## Use
Run the Python script from the terminal (or your IDE).  
Visit the web address that is printed in the terminal to use the tool.

_For more info regarding how Gradio works, please refer to the general README in this repository._
