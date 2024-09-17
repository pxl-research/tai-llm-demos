# LLM Chat Executable

TransformAI

## What's in this folder?

This folder contains code that can be built into a simple executable,
to create a standalone "application" that can be run on Windows, Mac or Linux
(depending on the platform you build it on).

**Warning**: this example is very basic and not fit for everyday use.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Also install [pyinstaller](https://pyinstaller.org/en/stable/installation.html)

## Use

To create the executable file run `pyinstaller --clean pixie_lite.spec` from a command prompt.
If all goes well this will produce a `build` and `dist` folder.
The (portable) executable will be in the `dist` folder.