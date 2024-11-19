import chromadb
import pymupdf4llm
from tqdm import tqdm

from applications.faq_tool.vectorstore.cdb_utilities import sanitize_filename, doc_to_chunks, repack_query_results


class ChromaDocumentStore:
    cdb_client: chromadb.ClientAPI

    def __init__(self, path=None):
        if path is None:
            self.cdb_client = chromadb.Client()  # in memory
        else:
            self.cdb_client = chromadb.PersistentClient(path=path)  # on disk

    def add_document(self, pdf_file_path: str, tqdm_func=tqdm):
        collection_name = sanitize_filename(pdf_file_path)

        current_document_list = self.list_documents()
        if collection_name in current_document_list:
            print(f'A document with this name is already in the collection: {collection_name}')
            # self.remove_document(collection_name)
            return

        md_text = pymupdf4llm.to_markdown(pdf_file_path)

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
        collections_list = self.cdb_client.list_collections()
        names = []
        for collection in collections_list:
            names.append([collection.name])
        return names

    def query_store(self, query: str):
        collections = self.cdb_client.list_collections()
        all_results = []
        for collection in collections:
            self.cdb_client.get_collection(collection.name)
            result = collection.query(
                query_texts=[query],
                n_results=5,
            )
            repacked = repack_query_results(result)
            all_results = all_results + repacked

        # sort results by distance
        return sorted(all_results, key=lambda r: r['distances'])
