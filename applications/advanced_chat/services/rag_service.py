"""
RAG Service: Document indexing and retrieval.
"""
from pathlib import Path
from typing import List, Dict, Any

from utils.chroma_store import ChromaDocumentStore
from utils.text_processing import document_to_markdown, chunk_markdown
from utils.config import RAG_DB_PATH


class RAGService:
    """Manages RAG document indexing and retrieval."""

    def __init__(self):
        """Initialize RAG service."""
        self.store = ChromaDocumentStore(path=str(RAG_DB_PATH))

    def add_document(self, file_path: str) -> bool:
        """
        Add a document to the RAG store.

        Args:
            file_path: Path to document file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert document to markdown
            markdown_content = document_to_markdown(file_path)

            # Get document name
            doc_name = Path(file_path).stem

            # Chunk the document
            chunks = chunk_markdown(markdown_content, chunk_size=500, overlap=50)

            # Create metadata for chunks
            meta_infos = []
            for i, chunk in enumerate(chunks):
                meta_infos.append({
                    'id': f'{doc_name}_{i}',
                    'document_name': doc_name,
                    'chunk_number': i,
                    'file_path': file_path
                })

            # Add to store
            self.store.add_document(doc_name, chunks, meta_infos)

            return True

        except Exception as e:
            import traceback
            print(f"Error adding document: {e}")
            print(traceback.format_exc())
            return False

    def query(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the RAG store.

        Args:
            query: Query string
            num_results: Number of results to return

        Returns:
            List of relevant document chunks
        """
        try:
            results = self.store.query_store(query, amount=num_results)
            return results
        except Exception as e:
            print(f"Error querying RAG store: {e}")
            return []

    def list_documents(self) -> List[str]:
        """
        List all indexed documents.

        Returns:
            List of document names
        """
        return self.store.list_documents()

    def remove_document(self, document_name: str) -> bool:
        """
        Remove a document from the RAG store.

        Args:
            document_name: Name of document to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            self.store.remove_document(document_name)
            return True
        except Exception as e:
            print(f"Error removing document: {e}")
            return False

    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get context string for including in prompts.

        Args:
            query: Query to search for
            max_tokens: Maximum tokens to include

        Returns:
            Formatted context string
        """
        results = self.query(query, num_results=5)

        if not results:
            return ""

        context_lines = ["# Retrieved Documents:"]
        token_count = 0

        for result in results:
            doc_name = result.get('metadata', {}).get('document_name', 'unknown')
            content = result.get('document', '')[:500]  # Limit chunk size

            chunk = f"\n**From {doc_name}:**\n{content}\n"
            context_lines.append(chunk)

            # Rough token estimate (1 token ~ 4 chars)
            token_count += len(chunk) // 4

            if token_count > max_tokens:
                break

        return ''.join(context_lines)
