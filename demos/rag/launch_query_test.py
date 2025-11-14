import json

from components.vectorstore.chroma_document_store import ChromaDocumentStore


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))


# cdb_store = ChromaDocumentStore()  # in memory
cdb_store = ChromaDocumentStore(path="store/")  # on disk

# TODO: add some files to the vector store first using the Gradio UI (launch_upload_ui.py)

# perform a document search on the vector database
query = "Hoe moet ik een dossier opsplitsen?"

print(query)
results = cdb_store.query_store(query)
pretty_print(results[:3])
