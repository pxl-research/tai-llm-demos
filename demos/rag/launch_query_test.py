import json

from demos.components.chroma_document_store import ChromaDocumentStore


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))


# cdb_store = ChromaDocumentStore()  # in memory
cdb_store = ChromaDocumentStore(path="store/")  # on disk

# TODO: add some files to the vector store first using the Gradio UI (launch_upload_ui.py)

# perform a document search on the vector database
query = "Wat is het gevolg van nonchalant loggen?"

print(query)
results = cdb_store.query_store(query)
pretty_print(results[:5])
