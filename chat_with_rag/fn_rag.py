import os
import sys

import chromadb
from dotenv import load_dotenv

sys.path.append('../')

from chat_with_rag.fn_chromadb import query_all_documents

load_dotenv()

cdb_path = os.getenv("CHROMA_LOCATION")
cdb_client = chromadb.PersistentClient(path=cdb_path)  # on disk

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
    results = query_all_documents(cdb_client, query)
    return results[:5]
