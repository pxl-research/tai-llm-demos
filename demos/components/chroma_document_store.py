import os
import re

import chromadb
from tqdm import tqdm

from demos.rag.fn_pdf_utils import (
    pdf_to_text,
    pages_to_chunks
)


# helper methods
def sanitize_filename(full_file_path):
    cleaner_name = os.path.basename(full_file_path)  # remove path
    cleaner_name = os.path.splitext(cleaner_name)[0]  # remove extension
    cleaner_name = sanitize_string(cleaner_name)
    return cleaner_name[:60]  # crop it


def sanitize_string(some_text):
    cleaner_name = some_text.strip()
    cleaner_name = cleaner_name.replace(" ", "_")  # spaces to underscores
    cleaner_name = re.sub(r'[^a-zA-Z0-9_-]', '-', cleaner_name)  # replace invalid characters with spaces
    return cleaner_name


def repack_query_results(result):
    fields = ['distances', 'metadatas', 'embeddings', 'documents', 'uris', 'data']
    length = len(result['ids'][0])  # ids are always returned
    repacked = []
    for r in range(length):
        repacked_result = {'ids': result['ids'][0][r]}
        for field in fields:
            if result[field] is not None:
                repacked_result[field] = result[field][0][r]
        repacked.append(repacked_result)
    return repacked


# class
class ChromaDocumentStore:
    cdb_client: chromadb.ClientAPI

    def __init__(self, path=None):
        if path is None:
            self.cdb_client = chromadb.Client()  # in memory
        else:
            self.cdb_client = chromadb.PersistentClient(path=path)  # on disk

    def add_document(self, file_path: str, tqdm_func=tqdm):
        collection_name = sanitize_filename(file_path)

        page_list = pdf_to_text(file_path)
        chunks, chunk_ids, meta_infos = pages_to_chunks(page_list, collection_name)
        print(f"Split {len(page_list)} pages into {len(chunk_ids)} chunks for '{collection_name}'")

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
        collections_list = self.cdb_client.list_collections()
        names = []
        for collection in collections_list:
            names.append(collection.name)
        return names

    def query_store(self, query: str):
        collections = self.cdb_client.list_collections()
        all_results = []
        for collection in collections:
            print(f"Looking up in '{collection.name}'")
            self.cdb_client.get_collection(collection.name)
            result = collection.query(
                query_texts=[query],
                n_results=5,
            )
            repacked = repack_query_results(result)
            all_results = all_results + repacked

        # sort results by distance
        return sorted(all_results, key=lambda r: r['distances'])
