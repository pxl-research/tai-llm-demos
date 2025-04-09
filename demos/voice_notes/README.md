# Voice Note Summary Demo
TransformAI

## What's in this folder?
This folder contains a basic **voice note summary** example:

- `summarizer.py`: The Gradio tool (web interface) for transcribing and summarizing audio files.

- `llm_functions.py`: Contains the LLM summary prompt and methods, using OpenRouter for accessing the language model.

## Configuration
To install the necessary libraries, use `pip install -r requirements.txt`

**WARNING**: these libraries are quite large and may take a while to install.

If you do not have an NVIDIA graphics card, the transcription will be performed on the CPU and may take a relatively long time.

Please create an `.env` file with the same structure as the provided `.env.example` file, and enter your personal OpenRouter **API key** and **endpoint** therein.

## Use
Run the `summarizer.py` script from the terminal (or your IDE). Visit the web address that is printed in the terminal to use the tool.

_For more info regarding how Gradio works, please refer to the general README in this repository._
