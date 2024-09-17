import os
import re
import sys

import gradio as gr
from dotenv import load_dotenv
from tqdm import tqdm

from demos.rag.chroma_document_store import ChromaDocumentStore

sys.path.append('../')

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


# https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
def sanitize_filename(full_file_path):
    cleaner_name = os.path.basename(full_file_path)  # remove path
    cleaner_name = os.path.splitext(cleaner_name)[0]  # remove extension
    cleaner_name = sanitize_string(cleaner_name)
    return cleaner_name[:60]  # crop it


def sanitize_string(some_text):
    cleaner_name = some_text.strip()
    cleaner_name = cleaner_name.replace(" ", "_")  # spaces to underscores
    cleaner_name = re.sub(r'[^a-zA-Z0-9_-]', '-', cleaner_name)  # replace invalid characters with spaces
    return cleaner_name


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
