import os
import sys

from dotenv import load_dotenv

sys.path.append('../')
sys.path.append('../../')

from demos.components.vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def list_documents():
    try:
        return cdb_store.list_documents()
    except Exception as e:
        print(e)
        return []


def lookup_in_documentation(query):
    try:
        results = cdb_store.query_store(query)
        return results[:5]
    except Exception as e:
        print(e)
        return []
