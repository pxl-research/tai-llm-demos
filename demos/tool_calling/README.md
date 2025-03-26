# LLM Chat with Tool Calling

TransformAI

## What's in this folder?

This repository contains an example chatbot using [OpenRouter](https://openrouter.ai/) with "**tool calling**".

- the `tool_descriptors.py` file contains the JSON descriptions of several of the callable functions
- the files starting with `tool_...` contain an implementation for the callable functions.
  E.g. a stub for the weather methods, a method for calling rag functions (see `rag` example),
  a search tool (uses Google Search API), and a website download tool. 
- the `descriptors_fileio.py` file contains the JSON descriptions for the file I/O tools defined in `tools_fileio.py`.
- the `tools_fileio.py` file provides functions for interacting with the file system, such as listing files, reading and writing file contents, creating folders, and deleting files/folders.

N.B.: This program is a little longer and more convoluted because it uses _streaming responses_ from the LLM.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file,
and enter your personal OpenRouter **api key** (and **endpoint**) therein.  
Ensure the `.env` file is properly configured when using file i/o, especially the `ALLOWED_FOLDER` variable, 
which restricts the file system access of the file I/O tools for security reasons.

## Use

Run the python script from the terminal (or your IDE).

You can ask a question like _"What's the weather like in Amsterdam?"_ and the LLM will
try and call the relevant methods to get sufficient information to answer these questions.

If you have added pdf files to the document store (see `rag` example),
you can also ask the LLM questions about the contents of these documents.

_For info regarding how Gradio works, please refer to the general README in this repository._

## Expanding this example

The `get_current_temperature` and `get_current_rainfall` functions in `tools_weather.py` are currently stubs and should be replaced with actual implementations that fetch weather data from an external API or other source.

To add extra tools/functions, you need to do the following:

- Implement the tool's functionality in a new `tools_*.py` file.
- Create a descriptor for the tool in `tool_descriptors.py` or a separate `descriptors_*.py` file.
- Import the tool's function(s) and descriptor(s) in `chat_with_tool_calling.py` and add the descriptor to the `tool_list`.
  Try and make sure your IDE does not remove them when they are not being called explicitly.
