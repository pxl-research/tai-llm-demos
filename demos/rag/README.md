# RAG Demo

## What's in this folder?

This folder contains **only the document retrieval part** of a RAG system.

It is a minimal example implemented using [ChromaDB](https://docs.trychroma.com/) for vector storage and [markitdown](https://github.com/jordaneremieff/markitdown) for document parsing.

`launch_upload_ui.py` contains a simple Gradio webpage to upload and parse documents into the vector database. Add one or more documents (PDFs, Word documents, PowerPoint presentations, Excel spreadsheets) here. Document processing can take a while depending on the size of the documents and the performance of your system.

`launch_query_test.py` contains a (text only) Python script to query the vector database.

## Configuration

To install the necessary libraries, use `pip install -r requirements.txt`

## Use

1.  Run `launch_upload_ui.py` to upload and process documents. This will start a Gradio interface.
2.  Once documents are uploaded, run `launch_query_test.py` to query the vector database.

_For more info regarding how Gradio works, please refer to the general README in this repository._
