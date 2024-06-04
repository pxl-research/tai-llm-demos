import json

import chromadb

from fn_chromadb import query_all_documents, add_pdf_to_db


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))


cdb_client = chromadb.Client()  # in memory
# cdb_client = chromadb.PersistentClient(path="store/")  # on disk

# NOTE: adding files can now be done with gradio UI
add_pdf_to_db(cdb_client, "arbeidsregelement", "documents/arbeidsreglement.pdf")

# perform a search on the vector database
query = "Hoeveel uur mag ik werken per dag?"

print(query)
results = query_all_documents(cdb_client, query)
pretty_print(results[:5])
