import chromadb

cdb_client = chromadb.PersistentClient(path="../rag_demo/store/")  # on disk

descriptor_lookup_in_company_docs = {
    "type": "function",
    "function": {
        "name": "lookup_in_company_docs",
        "description": "Get snippets from documentation of company procedures. Use this as a search engine and put in natural language questions or statements as search queries. "
                       "The method will return an array of JSON objects, containing a 'documents' part with the associated text, "
                       "a 'distances' array indicating how well the info matches your question (smaller numbers are better), "
                       "and a 'metadatas' object with some info about the text chunks: document name, page number, and a paragraph (chunk) number. "
                       "Please always include the document name and page number when referencing this documentation.",
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
    print(f"Searching in company docs: '{query}'")
    collections = cdb_client.list_collections()
    all_results = []
    for collection in collections:
        print(f"Looking up in '{collection.name}'")
        cdb_client.get_collection(collection.name)
        results = collection.query(
            query_texts=[query],
            n_results=3,
        )
        all_results.append(results)
    # TODO: grab surrounding chunks
    return all_results
