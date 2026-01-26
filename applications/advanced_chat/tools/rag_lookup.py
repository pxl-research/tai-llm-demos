"""
RAG Lookup Tool: Search uploaded documents.
"""
import sys
from typing import Dict, Any
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_service import RAGService


# Global RAG service instance - will be set by launch_ui.py
_rag_service = None


def set_rag_service(rag_service: RAGService):
    """Set the shared RAG service instance."""
    global _rag_service
    _rag_service = rag_service


def get_rag_service() -> RAGService:
    """Get the RAG service instance."""
    global _rag_service
    if _rag_service is None:
        # Fallback: create a new instance if none was set
        _rag_service = RAGService()
    return _rag_service


def lookup_in_documentation(query: str) -> Dict[str, Any]:
    """
    Search for information in uploaded documents.

    Args:
        query: Search query

    Returns:
        Dictionary with search results
    """
    try:
        rag_service = get_rag_service()
        results = rag_service.query(query, num_results=3)

        if not results:
            return {
                'query': query,
                'found': False,
                'results': [],
                'message': 'No relevant documents found'
            }

        formatted_results = []
        for result in results:
            formatted_results.append({
                'document': result.get('document', '')[:1000],
                'distance': result.get('distance', 0),
                'metadata': result.get('metadata', {})
            })

        return {
            'query': query,
            'found': True,
            'results': formatted_results,
            'message': f'Found {len(formatted_results)} relevant results'
        }

    except Exception as e:
        return {
            'query': query,
            'found': False,
            'results': [],
            'error': str(e)
        }


def list_documents() -> Dict[str, Any]:
    """
    List all indexed documents.

    Returns:
        Dictionary with document list
    """
    try:
        rag_service = get_rag_service()
        documents = rag_service.list_documents()

        return {
            'documents': documents,
            'count': len(documents),
            'message': f'{len(documents)} documents available'
        }

    except Exception as e:
        return {
            'documents': [],
            'error': str(e)
        }


# Tool descriptors for LLM
rag_lookup_descriptor = {
    "type": "function",
    "function": {
        "name": "lookup_in_documentation",
        "description": "Search through uploaded documents for information related to your query. Use natural language questions to search. Returns relevant text excerpts from the documents with metadata about where they came from.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find in documents"
                }
            },
            "required": ["query"]
        }
    }
}

list_docs_descriptor = {
    "type": "function",
    "function": {
        "name": "list_documents",
        "description": "Get a list of all documents that have been uploaded and indexed in the knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# Combined list for easy registration
rag_descriptors = [rag_lookup_descriptor, list_docs_descriptor]
