import os
import sys

import gradio as gr
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.append('../')
sys.path.append('../../')

from demos.components.vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def on_file_uploaded(uploaded_files, progress=gr.Progress(track_tqdm=True)):
    """Add uploaded files to the ChromaDB store and return updated collection names."""
    for file_path in uploaded_files:
        try:
            cdb_store.add_document(file_path, tqdm)
        except Exception as e:
            print(e)
            pass
    collection_names = list_collections()
    return [None, collection_names]


def list_collections():
    """Return a list of document collections in the ChromaDB store."""
    try:
        return cdb_store.list_documents()
    except Exception as e:
        print(e)
        return []


def remove_collection(collection_name):
    """Remove a document collection from the ChromaDB store and return updated names."""
    try:
        cdb_store.remove_document(collection_name)
    except Exception as e:
        print(e)
        pass
    collection_names = list_collections()
    return collection_names
