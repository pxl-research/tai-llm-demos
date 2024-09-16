import json

import chromadb

from fn_chromadb import query_all_documents, add_pdf_to_db


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))


# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path="store/")  # on disk

# TODO: add some files to the vector store first using the Gradio UI (launch_upload_ui.py)

# perform a document search on the vector database
query = "Hoeveel uren mag een lector werken per dag?"

print(query)
results = query_all_documents(cdb_client, query)
pretty_print(results[:5])
