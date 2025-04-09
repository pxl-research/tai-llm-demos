# LLM Chat Executable

TransformAI

## What's in this folder?

This folder contains code that can be built into a simple executable,
to create a standalone "application" that can be run on Windows, Mac or Linux
(depending on the platform you build it on).

**Warning**: this example is very basic and not fit for everyday use.

The GUI is built using `wxPython`.

## Contents

*   `pixie_lite.py`: The main application script.
*   `fn_utils.py`: Utility functions (e.g., Markdown to HTML conversion).
*   `fn_llm_or.py`: Handles communication with the OpenRouter LLM.
*   `assets/`: Contains asset files:
    *   `.env`: Stores the OpenRouter API key.
    *   `header.html`: HTML header for the web view.
    *   `README.md`: This README file (displayed in the application).
    *   `chat.png`: Application icon.

## Configuration

1.  Install the necessary libraries using `pip install -r requirements.txt`.
2.  Install [PyInstaller](https://pyinstaller.org/en/stable/installation.html).
3.  Obtain an OpenRouter API key and place it in the `assets/.env` file.

## Use

1.  Navigate to the `gui` directory in your terminal.
2.  Run `pyinstaller --clean pixie_lite.spec` from the command prompt.
3.  If all goes well, this will produce a `build` and `dist` folder.
4.  The (portable) executable will be in the `dist` folder.
