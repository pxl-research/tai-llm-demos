import time

import chromadb

from class_based.superclasses.document_converter import DocumentConverter
from class_based.superclasses.retriever import Retriever
from class_based.superclasses.textsplitter import TextSplitter
from class_based.superclasses.vectorstore import VectorStore
from class_based.vectorstores.chromadb.utils import repack_results, cleanup_filename


class ChromaDbVectorStore(VectorStore, Retriever):

    def __init__(self,
                 document_converter: DocumentConverter,
                 textsplitter: TextSplitter):
        self.cdb_client = chromadb.Client()  # in memory
        # self.cdb_client = chromadb.PersistentClient(path="store/")  # on disk

        self.document_converter = document_converter
        self.textsplitter = textsplitter

    def add_document(self, file_path: str):
        # TODO: check if pdf

        start_time = time.time()
        page_list = self.document_converter.convert_to_markdown_pages(file_path)

        chunks = []
        meta_info = {'doc': file_path}
        page_nr = 0

        for page in page_list:
            page_nr = page_nr + 1
            meta_info['page_nr'] = page_nr
            page_chunks = self.textsplitter.split(page, meta_info=meta_info, index_offset=len(chunks))
            chunks.append(page_chunks)

        collection_name = cleanup_filename(file_path)
        print(f"Split {len(page_list)} pages into {len(chunks)} chunks for '{collection_name}'")

        # https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
        cdb_collection = self.cdb_client.create_collection(collection_name)
        # TODO: custom embedding function: https://cookbook.chromadb.dev/embeddings/bring-your-own-embeddings/#example-implementation

        chunk_texts: list[str] = []
        chunk_ids: list[str] = []
        meta_infos: list[dict] = []

        for chunk in chunks:
            chunk_texts.append(chunk['text'])
            chunk_ids.append(f"{chunk['id']}")
            meta_infos.append(chunk['meta'])

        total = len(chunks)
        for c in range(total):  # estimate about 220ms per chunk
            cdb_collection.add(
                documents=chunks[c],
                ids=chunk_ids[c],
                metadatas=meta_infos[c]
            )
        duration = (time.time() - start_time)  # convert to ms
        print(f"Added {len(chunks)} chunks to chroma db ({round(duration)} sec)")

    def delete_document(self, file_path: str):
        collection_name = cleanup_filename(file_path)
        self.cdb_client.delete_collection(collection_name)

    # https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections

    def retrieve_chunks(self, question: str, n_chunks: int = 5) -> list:
        collections = self.cdb_client.list_collections()
        all_results = []
        for collection in collections:
            print(f"Looking up in '{collection.name}'")
            self.cdb_client.get_collection(collection.name)
            result = collection.query(
                query_texts=[question],
                n_results=5,
            )
            repacked = repack_results(result)
            all_results = all_results + repacked

        # TODO: grab surrounding chunks ?

        # sort results by distance
        return sorted(all_results, key=lambda r: r['distances'])
