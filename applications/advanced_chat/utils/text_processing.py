"""
Text processing utilities - simplified from components/text_utils/
Self-contained for this application.
"""
import re
from markitdown import MarkItDown


def document_to_markdown(doc_filename: str) -> str:
    """
    Convert a document (docx, pptx, xlsx, pdf) to Markdown text.
    """
    mid = MarkItDown(enable_plugins=False)
    conversion = mid.convert(doc_filename)
    return conversion.text_content


def chunk_markdown(md_text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split markdown text into chunks with optional overlap.
    Simplified version for this application.

    Args:
        md_text: Markdown text to split
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_len = len(md_text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end == text_len:
            chunk = md_text[start:end]
            chunks.append(chunk.strip())
            break

        # Find last whitespace before chunk_size to avoid breaking words
        last_space = md_text.rfind(' ', start, end)
        if last_space == -1:
            chunk_end = end
        else:
            chunk_end = last_space

        chunk = md_text[start:chunk_end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = chunk_end - overlap if overlap > 0 else chunk_end

    return chunks
