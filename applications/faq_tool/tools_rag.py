import os

from dotenv import load_dotenv

from vectorstore.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
print(f'Location of RAG DB: {cdb_path}')
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk


def list_documents():
    return cdb_store.list_documents()


def lookup_in_documentation(query):
    print(f"Searching in documentation: '{query}'")
    results = cdb_store.query_store(query, amount=5)
    print(f'Retrieved {len(results)} results')
    return results
