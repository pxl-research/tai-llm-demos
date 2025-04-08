import os
import sys

import gradio as gr
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.append('../')
sys.path.append('../../')

from applications.faq_tool.vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def on_file_uploaded(file_list, progress=gr.Progress(track_tqdm=True)):
    for file_path in file_list:
        cdb_store.add_document(file_path, tqdm)
    names = list_collections()
    return [None, names]


def list_collections():
    return cdb_store.list_documents()


def remove_collection(collection_name):
    cdb_store.remove_document(collection_name)
    names = list_collections()
    return names
