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


def query_all_documents(cdb_client, queries):
    collections = cdb_client.list_collections()
    all_results = []
    for collection in collections:
        print(f"Looking up in '{collection.name}'")
        cdb_client.get_collection(collection.name)
        results = collection.query(
            query_texts=queries,
            n_results=3,
        )
        all_results.append(results)

    return all_results


# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path="store/")  # on disk

# add_pdf_to_db(cdb_client, "focusproject", "documents/focusproject.pdf")
# add_pdf_to_db(cdb_client, "dienstverlening", "documents/dienstverlening.pdf")
# add_pdf_to_db(cdb_client, "speerpuntprojecten", "documents/speerpuntprojecten.pdf")
# add_pdf_to_db(cdb_client, "onderwijsinnovatiefonds", "documents/onderwijsinnovatiefonds.pdf")
# add_pdf_to_db(cdb_client, "arbeidsregelement", "documents/arbeidsreglement.pdf")

# perform a search on the vector database
queries = ["Wat is een focusproject precies?",
           "Wat is de prijs van 1kg aardappelen?",
           "Hoeveel uur mag ik werken per dag?"]
pprint(queries)

results = query_all_documents(cdb_client, queries)
pprint(results)

# for result in results:
#     pprint(result['distances'])
#     pprint(result['metadatas'])
#     print('------------------')
