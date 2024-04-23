import json

import chromadb

from fn_chromadb import query_all_documents, add_pdf_to_db


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))


cdb_client = chromadb.Client()  # in memory
# cdb_client = chromadb.PersistentClient(path="store/")  # on disk

add_pdf_to_db(cdb_client, "focusproject", "documents/focusproject.pdf")
# add_pdf_to_db(cdb_client, "dienstverlening", "documents/dienstverlening.pdf")
# add_pdf_to_db(cdb_client, "speerpuntprojecten", "documents/speerpuntprojecten.pdf")
# add_pdf_to_db(cdb_client, "onderwijsinnovatiefonds", "documents/onderwijsinnovatiefonds.pdf")
# add_pdf_to_db(cdb_client, "arbeidsregelement", "documents/arbeidsreglement.pdf")

# perform a search on the vector database
query = "Wat is een focusproject precies?"
# query = "Wat is de prijs van 1kg aardappelen?"
# query = "Hoeveel uur mag ik werken per dag?"

print(query)
results = query_all_documents(cdb_client, query)
pretty_print(results[:5])
