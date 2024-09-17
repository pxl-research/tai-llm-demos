import os
import sys

from dotenv import load_dotenv

sys.path.append('../')

from demos.rag.chroma_document_store import ChromaDocumentStore

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_store = ChromaDocumentStore(path=cdb_path)  # on disk

tool_rag_descriptor = {
    "type": "function",
    "function": {
        "name": "lookup_in_documentation",
        "description": "Get snippets from documents related to the domain you operate in."
                       "Use this as a search engine and put in natural language questions or statements as search queries. "
                       "The method will return an array of JSON objects, containing a 'documents' part with the associated text, "
                       "a 'distances' value indicating how well the info matches your question (smaller numbers are better), "
                       "and a 'metadatas' object with some info about the text chunks: document name, page number, and a paragraph (chunk) number. "
                       "Always include the document name and page number when referencing this documentation.",
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


def lookup_in_documentation(query):
    print(f"Searching in company docs: '{query}'")
    results = cdb_store.query_store(query)
    return results[:5]
