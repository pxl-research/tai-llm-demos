import os
import sys

import gradio as gr
from dotenv import load_dotenv
from tqdm import tqdm

from components.text_utils.md_chunking import iterative_chunking
from components.text_utils.md_conversion import document_to_markdown
from components.text_utils.string_utils import sanitize_filename

sys.path.append('../')
sys.path.append('../../')

from components.vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def on_file_uploaded(uploaded_files, progress=gr.Progress(track_tqdm=True)):
    """Add uploaded files to the ChromaDB store and return updated collection names."""
    for file_path in uploaded_files:
        try:
            collection_name = sanitize_filename(file_path)
            md_text = document_to_markdown(file_path)
            chunks = iterative_chunking(md_text)
            meta_info = [{'source': file_path, 'id': f'chunk_{i}'} for i in range(len(chunks))]
            cdb_store.add_document(document_name=collection_name,
                                   chunks=chunks,
                                   meta_infos=meta_info,
                                   tqdm_func=tqdm)
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
