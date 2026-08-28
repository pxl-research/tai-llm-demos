"""
ChromaDB document store - simplified from components/vectorstore/chroma_document_store.py
Self-contained for this application.
"""
import re

import chromadb
from chromadb import QueryResult
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


def sanitize_collection_name(document_name: str) -> str:
    """Turn a filename into a valid Chroma collection name: 3-512 characters from
    [a-zA-Z0-9._-], starting and ending with an alphanumeric character."""
    name = re.sub(r'[^a-zA-Z0-9._-]+', '_', document_name.lower()).strip('._-')
    name = name[:512].rstrip('._-') or 'doc'
    return name.ljust(3, '0')


def warm_up_embeddings():
    """Load the default embedding model, downloading it from Chroma's S3 bucket if needed.

    That download has no timeout in Chroma itself, so triggering it once, eagerly, with
    visible status is better than having it silently stall during a user's first upload.
    """
    DefaultEmbeddingFunction()(['warm up'])


def repack_query_results(results: QueryResult):
    """Repack query results into a more usable format."""
    fields = ['ids', 'distances', 'metadatas', 'documents']
    length = len(results['ids'][0])
    repacked = []
    for r in range(length):
        repacked_result = {}
        for field in fields:
            if results[field] is not None:
                repacked_result[field[:-1]] = results[field][0][r]
        repacked.append(repacked_result)
    return repacked


class ChromaDocumentStore:
    """Simple ChromaDB document store."""

    def __init__(self, path=None):
        if path is None:
            print('WARNING: using in-memory ChromaDB, no persistence!')
            self.cdb_client = chromadb.Client()
        else:
            self.cdb_client = chromadb.PersistentClient(path=path)

    def add_document(self, document_name: str, chunks: list[str], meta_infos: list):
        """Add a document to the store."""
        collection_name = sanitize_collection_name(document_name)

        current_docs = self.list_documents()

        if collection_name in current_docs:
            print(f'Document already exists: {collection_name}')
            return

        cdb_collection = self.cdb_client.create_collection(collection_name)

        # One batched call lets Chroma embed all chunks in a single pass -- adding them
        # one at a time was ~4x slower for a 300-chunk document in testing, and made the
        # document appear (via list_documents) well before it was actually indexed, since
        # the collection is created upfront.
        cdb_collection.add(
            documents=chunks,
            ids=[meta_info['id'] for meta_info in meta_infos],
            metadatas=meta_infos
        )

    def remove_document(self, document_name: str):
        """Remove a document from the store."""
        self.cdb_client.delete_collection(document_name)

    def list_documents(self):
        """List all documents in the store."""
        collections = self.cdb_client.list_collections()
        return sorted([c.name for c in collections])

    def query_store(self, query: str, amount: int = 5):
        """Query the store for relevant documents."""
        all_results = []

        collections = self.cdb_client.list_collections()
        for collection in collections:
            results = collection.query(
                query_texts=[query],
                n_results=amount,
            )
            cleaned_results = repack_query_results(results)
            all_results.extend(cleaned_results)

        # Sort by distance
        all_results = sorted(all_results, key=lambda r: r['distance'])
        return all_results[:amount]
