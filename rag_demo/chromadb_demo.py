import time
from pprint import pprint

import chromadb

from pdf_utils import (pdf_to_text, pages_to_chunks)


def add_pdf_to_db(cdb_client, collection_name, file_path):
    start_time = time.time()  # estimate about 220ms per chunk

    page_list = pdf_to_text(file_path)
    print(f"Extracted {len(page_list)} pages from '{file_path}'")

    chunks, chunk_ids, meta_infos = pages_to_chunks(page_list, collection_name)
    print(f"Split {len(page_list)} pages into {len(chunk_ids)} chunks")

    # https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
    new_collection = cdb_client.create_collection(collection_name)
    new_collection.add(
        documents=chunks,
        ids=chunk_ids,
        metadatas=meta_infos
    )
    duration = (time.time() - start_time)  # convert to ms
    print(f"Added {len(chunk_ids)} chunks to chroma db ({round(duration)} sec)")


# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path="store/")  # on disk
collection_name = "arbeidsregelement"

# add_pdf_to_db(cdb_client, collection_name, "documents/ArbeidsreglementV8.pdf")

# perform a search on the vector database
queries = ["Hoeveel uur per dag mag ik werken?",
           "Wat is de prijs van 1kg aardappelen?",
           "Een telefoonnummer?"]
pprint(queries)  # estimate about 200ms per query

collection = cdb_client.get_collection(collection_name)
results = collection.query(
    query_texts=queries,
    n_results=5,
)

pprint(results['distances'])
pprint(results['ids'])

first_ids = []
for ids in results['ids']:
    print(ids[0])
    pprint(collection.get(ids=[ids[0]]))
