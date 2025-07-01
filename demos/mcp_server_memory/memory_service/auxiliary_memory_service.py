import os
import sys
from typing import List, Optional, Literal

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import DB_PATH, OPENROUTER_API_KEY
from db import SQLiteManager, ChromaManager
from utils import timestamp, format_response
from utils.summarizer import Summarizer

# Initialize database managers
sqlite_manager = SQLiteManager()
chroma_manager = ChromaManager()

# Initialize summarizer
summarizer = Summarizer(api_key=OPENROUTER_API_KEY)


def list_topics() -> List[dict]:
    """List all available topics/knowledge domains in the memory system.
    
    Returns:
        List[dict]: Available topics with counts and descriptions
    """
    try:
        topics = sqlite_manager.list_topics()

        return topics if topics else [
            format_response(success=True, message="No topics found")
        ]

    except Exception as e:
        return [format_response(
            success=False,
            message=f"Error listing topics: {str(e)}"
        )]


def get_status() -> dict:
    """Get memory system status and statistics.
    
    Returns:
        dict: Statistics about memory usage, counts, etc.
    """
    try:
        # Get SQLite statistics
        sqlite_stats = sqlite_manager.get_status()

        # Get ChromaDB information
        chroma_stats = chroma_manager.get_status()

        return format_response(
            success=True,
            message="Memory status retrieved successfully",
            data={
                "stats": {
                    **sqlite_stats,
                    **chroma_stats,
                    "db_path": DB_PATH,
                    "system_time": timestamp()
                }
            }
        )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error getting memory status: {str(e)}"
        )


def delete_empty_topic(
        topic_name: str
) -> dict:
    """Delete a topic from the system if it has no associated memory items.

    Args:
        topic_name: The name of the topic to delete.

    Returns:
        dict: Status of the deletion operation.
    """
    try:
        success = sqlite_manager.delete_topic_if_empty(topic_name)
        if success:
            return format_response(
                success=True,
                message=f"Topic '{topic_name}' deleted successfully because it was empty."
            )
        else:
            # Check if topic exists but is not empty
            topic_info = sqlite_manager.list_topics()
            topic_exists = False
            item_count = 0
            for topic in topic_info:
                if topic["name"] == topic_name:
                    topic_exists = True
                    item_count = topic["item_count"]
                    break

            if topic_exists and item_count > 0:
                return format_response(
                    success=False,
                    message=f"Topic '{topic_name}' could not be deleted because it is not empty. It contains {item_count} items."
                )
            else:
                return format_response(
                    success=False,
                    message=f"Topic '{topic_name}' not found."
                )
    except Exception as e:
        return format_response(
            success=False,
            message=f"Error deleting topic: {str(e)}"
        )


def summarize_memory(
        memory_id: Optional[str] = None,
        query: Optional[str] = None,
        topic: Optional[str] = None,
        summary_type: Literal["abstractive", "extractive", "query_focused"] = "abstractive",
        length: Literal["short", "medium", "detailed"] = "medium"
) -> dict:
    """Generate a summary of memory items.

    Args:
        memory_id: ID of a specific memory item to summarize.
        query: A query to find relevant memories to summarize.
        topic: A topic to find relevant memories to summarize.
        summary_type: The type of summary to generate.
        length: The desired length of the summary.

    Returns:
        dict: The generated summary or an error message.
    """
    if not any([memory_id, query, topic]):
        return format_response(
            success=False,
            message="At least one of memory_id, query, or topic must be provided."
        )

    content_to_summarize = ""
    if memory_id:
        item = sqlite_manager.get_memory(memory_id)
        if item:
            content_to_summarize = item["content"]
        else:
            return format_response(success=False, message=f"Memory item with ID {memory_id} not found.")
    elif query or topic:
        # Search for relevant memories (using full content embeddings for broader search)
        # Note: This might need refinement to search summary embeddings first for efficiency
        # and then retrieve full content for summarization.
        retrieved_memory_ids = chroma_manager.search_memories(query=query if query else "", max_results=10, topic=topic)

        if not retrieved_memory_ids:
            return format_response(success=True, message="No relevant memories found to summarize.")

        # Retrieve full content for summarization
        contents = []
        for mid in retrieved_memory_ids:
            item = sqlite_manager.get_memory(mid)
            if item:
                contents.append(item["content"])

        if not contents:
            return format_response(success=True, message="Could not retrieve content for relevant memories.")

        content_to_summarize = "\n\n".join(contents)

    if not content_to_summarize:
        return format_response(success=False, message="No content found to summarize.")

    try:
        generated_summary = summarizer.generate_summary(
            content_to_summarize,
            summary_type=summary_type,
            length=length,
            query=query if summary_type == "query_focused" else None
        )

        if generated_summary:
            return format_response(
                success=True,
                message="Summary generated successfully",
                data={"summary": generated_summary}
            )
        else:
            return format_response(
                success=False,
                message="Failed to generate summary. LLM might have encountered an issue or returned empty."
            )
    except Exception as e:
        return format_response(
            success=False,
            message=f"Error generating summary: {str(e)}"
        )
