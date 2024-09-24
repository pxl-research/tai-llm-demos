# LLM Chat with Tool Calling

TransformAI

## What's in this folder?

This repository contains an example chatbot using [OpenRouter](https://openrouter.ai/) with "**tool calling**".

- the `tools_descriptors.py` file contains the JSON descriptions of the callable functions

- the `tools_weather.py` and `tools_rag.py` file contain an implementation stub for the weather methods
  and an actual method for calling the rag functions (see `rag` example)

N.B.: This program is a little longer and more convoluted because it uses _streaming responses_ from the LLM.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file,
and enter your personal OpenRouter **api key** (and **endpoint**) therein.

## Use

Run the python script from the terminal (or your IDE).

You can ask a question like _"What's the weather like in Amsterdam?"_ and the LLM will
try and call the relevant methods to get sufficient information to answer these questions.

If you have added pdf files to the document store (see `rag` example),
you can also ask the LLM questions about the contents of these documents.

_For info regarding how Gradio works, please refer to the general README in this repository._

## Expanding this example

The weather methods are currently stubs;
you can implement them however you want (i.e. calling a local function or remote API).

To add extra functions, you need to do two things:

- add a "descriptor" of your function (see `tool_descriptors.py` for examples),
  and append it to the `tool_list` array

- import your function so it is visible in the `chat_with_tool_calling.py`.
  Try and make sure your IDE does not remove them when they are not being called explicitly.
