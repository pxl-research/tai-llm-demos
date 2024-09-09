import os
import re
import sys

import chromadb
import gradio as gr
from dotenv import load_dotenv

sys.path.append('../')

from demos.rag.fn_chromadb import add_pdf_to_db

load_dotenv()

# cdb_client = chromadb.Client()  # in memory
cdb_path = os.getenv("CHROMA_LOCATION")
cdb_client = chromadb.PersistentClient(path=cdb_path)  # on disk


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


def on_file_uploaded(file_list, progress=gr.Progress()):
    # TODO: check if file already in collection?
    for file_path in file_list:
        collection_name = sanitize_filename(file_path)
        add_pdf_to_db(cdb_client, collection_name, file_path, progress)
    names = list_collections()
    return [None, names]


def list_collections():
    collections_list = cdb_client.list_collections()
    names = []
    for collection in collections_list:
        names.append([collection.name])
    return names


def remove_collection(collection_name):
    cdb_client.delete_collection(collection_name)
    names = list_collections()
    return names
