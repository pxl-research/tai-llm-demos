import sys

import chromadb
from tqdm import tqdm

sys.path.append('../')
sys.path.append('../../')

from demos.components.vectorstore.vs_utilities import (sanitize_filename,
                                                       doc_to_chunks,
                                                       repack_query_results,
                                                       document_to_markdown)


class ChromaDocumentStore:
    cdb_client: chromadb.ClientAPI

    def __init__(self, path=None):
        if path is None:
            self.cdb_client = chromadb.Client()  # in memory
        else:
            self.cdb_client = chromadb.PersistentClient(path=path)  # on disk

    def add_document(self, document_path: str, tqdm_func=tqdm):
        collection_name = sanitize_filename(document_path)

        current_document_list = self.list_documents()
        if collection_name in current_document_list:
            print(f'A document with this name is already in the collection: {collection_name}')
            # self.remove_document(collection_name)
            return

        md_text = document_to_markdown(document_path)

        chunks, chunk_ids, meta_infos = doc_to_chunks(md_text, collection_name)
        # print(f"Split {len(file_content)} characters into {len(chunk_ids)} chunks for '{collection_name}'")

        cdb_collection = self.cdb_client.create_collection(collection_name)
        total = len(chunks)
        taqaddum = tqdm_func(range(total))
        for c in taqaddum:
            cdb_collection.add(
                documents=chunks[c],
                ids=chunk_ids[c],
                metadatas=meta_infos[c]
            )
            taqaddum.set_description(desc=collection_name)

    def remove_document(self, document_name):
        self.cdb_client.delete_collection(document_name)

    def list_documents(self):
        collections = self.cdb_client.list_collections()
        collection_names = []
        for collection in collections:
            collection_names.append(collection.name)
        return collection_names

    def query_store(self, query: str, amount: int = 5):
        collections = self.cdb_client.list_collections()
        all_results = []
        for collection in collections:
            collection = self.cdb_client.get_collection(collection.name)
            result = collection.query(
                query_texts=[query],
                n_results=amount,
            )
            repacked = repack_query_results(result)
            all_results = all_results + repacked

        # sort results by distance
        return sorted(all_results, key=lambda r: r['distances'])
