import os
import sys

from dotenv import load_dotenv

sys.path.append('../')

from demos.components.vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def list_documents():
    return cdb_store.list_documents()


def lookup_in_documentation(query):
    print(f"Searching in company docs: '{query}'")
    results = cdb_store.query_store(query)
    return results[:5]
