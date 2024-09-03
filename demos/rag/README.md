# RAG Demo

TransformAI

## What's in this folder?

This folder contains **only the document retrieval part** of a RAG system.

It is a minimal example implemented using [pyMuPDF](https://github.com/pymupdf/PyMuPDF)
and [ChromaDB](https://docs.trychroma.com/)

`launch_upload_ui.py` contains a simple Gradio webpage to upload (and parse) documents into the vector database.
Add one or more PDF documents here. Document processing can take a while depending on the performance of your system.

`launch_query_test.py` contains a (text only) Python script to query the vector database.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

## Use

Run these Python scripts from the terminal (or your IDE).

_For more info regarding how Gradio works, please refer to the general README in this repository._
