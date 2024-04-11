from pprint import pprint

import chromadb
from pypdf import PdfReader

page_texts = []
names = []
count = 0
reader = PdfReader("documents/ArbeidsreglementV8.pdf")

# process the file
for page in reader.pages:
    text = page.extract_text()  # get page from pdf
    page_texts.append(text)

    count = count + 1
    names.append(f"page_{count}")
print(f"Converted {count} pages from pdf to text")

# add the pages to the vector database
cdb_client = chromadb.Client()
collection = cdb_client.create_collection("arbeidsreglenemnt")

collection.add(
    documents=page_texts,
    ids=names
)
print(f"Added {count} pages to chroma db")

# perform a search on the vector database
results = collection.query(
    query_texts=["Hoeveel uur per dag mag ik werken?"],
    n_results=3,
)

pprint(results)
