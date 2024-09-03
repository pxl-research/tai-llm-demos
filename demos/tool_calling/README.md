# LLM Chat with Tool Calling

TransformAI

## What's in this folder?

This repository contains an example chatbot using [OpenRouter](https://openrouter.ai/) with "tool calling".

The `tools_weather.py` file contains both the JSON description of the functions and
an implementation stub for the actual methods.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file,
and enter your personal OpenRouter **api key** and **endpoint** therein.

## Use

Run the python script from the terminal (or your IDE).

_For more info regarding how Gradio works, please refer to the general README in this repository._
