from pprint import pprint

import chromadb
import fitz


def convert_pdf(filename):
    page_texts = []
    names = []
    count = 0
    reader = fitz.open(filename)

    for page in reader:  # estimate about 4ms per page
        text = page.get_text()  # convert page from pdf to text
        page_texts.append(text)
        count = count + 1
        names.append(f"page_{count}")  # generate some page names
        # TODO: add summary or other meta info
    print(f"Converted {count} pages from '{filename}'")
    return page_texts, names


page_texts, names = convert_pdf("documents/ArbeidsreglementV8.pdf")

# add the pages to the vector database
cdb_client = chromadb.Client()
# cdb_client = chromadb.PersistentClient(path="store/")
collection = cdb_client.create_collection("arbeidsreglenemnt")

# estimate about 320ms per page (!)
collection.add(
    documents=page_texts,
    ids=names
)
print(f"Added {len(names)} pages to chroma db")

# perform a search on the vector database
query = "Hoeveel uur per dag mag ik werken?"
print(f"Query: '{query}'")
# estimate about 200ms per query
results = collection.query(
    query_texts=[query],
    n_results=3,
)

pprint(results['distances'])
pprint(results['ids'])
