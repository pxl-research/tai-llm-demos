import time
from pprint import pprint

import chromadb
import fitz


def convert_pdf(filename):
    chunk_list = []
    chunk_meta_list = []
    chunk_id_list = []
    page_nr = 0

    reader = fitz.open(filename)
    for page in reader:  # estimate about 4ms per page
        page_nr = page_nr + 1  # count pages
        text = page.get_text()  # convert page from pdf to text

        chunks = text.split('.')
        chunk_nr = 0
        for chunk in chunks:
            if len(chunk) > 5:  # no tiny chunks please
                chunk_nr = chunk_nr + 1
                chunk_list.append(chunk)
                meta = {'page': page_nr, 'chunk': chunk_nr}
                chunk_meta_list.append(meta)
                chunk_id_list.append(f"p{page_nr}_c{chunk_nr}")
        # TODO: add summary or other meta info
    print(f"Converted {page_nr} pages from '{filename}' into {len(chunk_id_list)} chunks")
    return chunk_list, chunk_id_list, chunk_meta_list


def add_pdf_to_db(cdb_client, collection_name, file_name):
    start_time = time.time()  # estimate about 220ms per chunk
    new_collection = cdb_client.create_collection(collection_name)
    chunks, chunk_ids, meta_infos = convert_pdf(file_name)
    new_collection.add(
        documents=chunks,
        ids=chunk_ids,
        metadatas=meta_infos
    )
    duration = (time.time() - start_time) * 1000  # convert to ms
    print(f"Added {len(chunk_ids)} chunks to chroma db ({round(duration)}ms)")


# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path="store/")  # on disk
collection_name = "arbeidsregelement"

# add_pdf_to_db(cdb_client, collection_name, "documents/ArbeidsreglementV8.pdf")

# perform a search on the vector database
queries = ["Hoeveel uur per dag mag ik werken?",
           "Wat is de prijs van 1kg aardappelen",
           "Wat is een Toezichthoudend personeelslid?"]
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
