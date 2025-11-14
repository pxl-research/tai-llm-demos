import sys

import chromadb
from chromadb import QueryResult
from tqdm import tqdm

sys.path.append('../')
sys.path.append('../../')

from demos.components.text_utils.string_utils import clean_up_string


def repack_query_results(results: QueryResult):
    # not included in mapping: 'uris', 'embeddings', 'data' , 'included'
    fields = ['ids', 'distances', 'metadatas', 'documents']
    length = len(results['ids'][0])  # ids are always returned
    repacked = []
    for r in range(length):
        repacked_result = {}
        for field in fields:
            if results[field] is not None:
                repacked_result[field[:-1]] = results[field][0][r]
        repacked.append(repacked_result)
    return repacked


class ChromaDocumentStore:
    cdb_client: chromadb.ClientAPI

    def __init__(self, path=None):
        if path is None:
            print('WARNING: using in-memory ChromaDB, no persistence!')
            self.cdb_client = chromadb.Client()  # in memory
        else:
            self.cdb_client = chromadb.PersistentClient(path=path)  # on disk

    def add_document(self, document_name: str,
                     chunks: list[str],
                     meta_infos: list,
                     tqdm_func=tqdm):
        collection_name = clean_up_string(document_name)

        current_document_list = self.list_documents()
        if collection_name in current_document_list:
            print(f'A document with this name is already in the collection: {collection_name}')
            # self.remove_document(collection_name)
            return

        # create a new collection for this document
        cdb_collection = self.cdb_client.create_collection(collection_name)

        taqaddum = tqdm_func(range(len(chunks)))
        taqaddum.set_description(desc=collection_name)
        for c in taqaddum:
            # add each chunk with its metadata
            cdb_collection.add(
                documents=chunks[c],
                ids=meta_infos[c]['id'],
                metadatas=meta_infos[c]
            )

    def remove_document(self, document_name):
        self.cdb_client.delete_collection(document_name)

    def list_documents(self):
        collections = self.cdb_client.list_collections()
        collection_names = []
        for collection in collections:
            collection_names.append(collection.name)
        collection_names.sort()
        return collection_names

    def query_store(self, query: str, amount: int = 5):
        all_results: list = []

        collections = self.cdb_client.list_collections()
        for collection in collections:
            results = collection.query(
                query_texts=[query],
                n_results=amount,
            )
            cleaned_results = repack_query_results(results)
            all_results.extend(cleaned_results)

        # sort results by distance
        sorted(all_results, key=lambda r: r['distance'])
        return all_results[:amount]
