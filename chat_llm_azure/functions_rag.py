import chromadb

cdb_client = chromadb.PersistentClient(path="../rag_demo/store/")  # on disk
collection_name = "arbeidsregelement"  # TODO: what if there are multiple collections?

descriptor_lookup_in_company_docs = {
    "type": "function",
    "function": {
        "name": "lookup_in_company_docs",
        "description": "Get snippets from documentation of company procedures. Use this as a search engine and put in natural language questions or statements as search queries. "
                       "The method will return an array of JSON objects, containing a 'documents' part with the associated text, and a 'metadatas' object with some info about the text chunks (e.g. page number). "
                       "Please always include the page number when referencing this documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "A natural language question about company rules or policies"}
            },
            "required": ["query"],
        },
    }
}


def lookup_in_company_docs(query):
    print(f"lookup_in_company_docs: '{query}'")
    collection = cdb_client.get_collection(collection_name)
    results = collection.query(
        query_texts=[query],
        n_results=3,
    )
    chunks = []
    for ids in results['ids']:
        for tmp_id in ids:
            chunk = collection.get(tmp_id)
            chunks.append(chunk)
    # TODO: grab surrounding chunks
    return chunks
