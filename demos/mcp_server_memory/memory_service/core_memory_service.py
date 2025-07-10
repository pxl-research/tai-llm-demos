import os
import sys
from typing import List, Optional, Literal

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import OPENROUTER_API_KEY
from db import SQLiteManager, ChromaManager
from utils import create_memory_id, timestamp, format_response
from utils.summarizer import Summarizer

# Initialize database managers
sqlite_manager = SQLiteManager()
chroma_manager = ChromaManager()

# Initialize summarizer
summarizer = Summarizer(api_key=OPENROUTER_API_KEY)


def initialize_memory(reset: bool) -> dict:
    """Initialize or reset the memory system databases.
    
    Args:
        reset: Whether to reset existing memory databases.
        
    Returns:
        dict: Initialization status
    """
    try:
        # Initialize SQLite
        sqlite_success = sqlite_manager.initialize(reset)

        # Initialize ChromaDB
        chroma_success = chroma_manager.initialize(reset)

        if sqlite_success and chroma_success:
            return format_response(
                success=True,
                message="Memory system initialized successfully",
                data={"reset": reset}
            )
        else:
            return format_response(
                success=False,
                message="Error initializing memory system",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success
                }
            )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error initializing memory system: {str(e)}"
        )


def store_memory(
        content: str,
        topic: str,
        tags: List[str] = []
) -> dict:
    """Store new information in the persistent memory system.
    
    Args:
        content: The text content to store in memory.
        topic: The primary topic or category for this content.
        tags: Optional list of tags for better retrieval.
        
    Returns:
        dict: Status and ID of the stored content
    """
    try:
        memory_id = create_memory_id()
        now = timestamp()

        # Store in SQLite
        sqlite_success = sqlite_manager.store_memory(memory_id, content, topic, tags)

        # Store in ChromaDB
        chroma_success = chroma_manager.store_memory(memory_id, content, topic, tags)

        # Update topic in ChromaDB
        topic_success = chroma_manager.update_topic(topic, tags)

        # Generate and store summary
        generated_summary = summarizer.generate_summary(content, summary_type="abstractive", length="medium")

        summary_stored = False
        summary_embedding_stored = False
        summary_id = create_memory_id()

        if generated_summary:
            summary_stored = sqlite_manager.store_summary(summary_id,
                                                          memory_id,
                                                          "abstractive_medium",
                                                          generated_summary)
            summary_embedding_stored = chroma_manager.store_summary_embedding(
                summary_id,
                generated_summary,
                {"memory_id": memory_id, "summary_type": "abstractive_medium", "topic": topic}
            )
        else:
            print(
                f"Warning: Failed to generate summary for memory_id {memory_id}. Original content stored without summary.")

        if sqlite_success and chroma_success:
            return format_response(
                success=True,
                message="Content stored successfully",
                data={
                    "memory_id": memory_id,
                    "topic": topic,
                    "tags": tags,
                    "timestamp": now,
                    "summary": {
                        "summary_generated": bool(generated_summary),
                        "summary_stored": summary_stored,
                        "summary_embedding_stored": summary_embedding_stored,
                        "summary_id": summary_id
                    }
                }
            )
        else:
            return format_response(
                success=False,
                message="Error storing content",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success,
                    "topic_success": topic_success,
                    "summary": {
                        "summary_generated": bool(generated_summary),
                        "summary_stored": summary_stored,
                        "summary_embedding_stored": summary_embedding_stored,
                        "summary_id": summary_id
                    }
                }
            )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error storing content: {str(e)}"
        )


def retrieve_memory(
        query: str,
        max_results: int = 5,
        topic: Optional[str] = None,
        return_type: Literal["full_text", "summary", "both"] = "full_text"
) -> List[dict]:
    """Retrieve information from memory using semantic search.
    
    Args:
        query: The search query to find relevant information.
        max_results: Maximum number of results to return.
        topic: Optional topic to restrict search to.
        return_type: The type of content to return (full_text, summary, or both).
        
    Returns:
        List[dict]: List of matching memory items with content and metadata
    """
    try:
        # Prioritize semantic search on summaries for efficiency
        summary_ids = chroma_manager.search_summary_embeddings(query, max_results, topic)
        memory_items = []
        for summary_id in summary_ids:
            summary_item = sqlite_manager.get_summary_by_id(summary_id)
            if summary_item:
                memory_id = summary_item["memory_id"]
                full_memory_item = sqlite_manager.get_memory(memory_id)

                if full_memory_item:
                    result_data = {
                        "id": memory_id,
                        "topic": full_memory_item["topic_name"],
                        "tags": full_memory_item["tags"],
                        "created_at": full_memory_item["created_at"],
                        "updated_at": full_memory_item["updated_at"]
                    }

                    if return_type == "full_text":
                        result_data["content"] = full_memory_item["content"]
                    elif return_type == "summary":
                        result_data["summary"] = summary_item["summary_text"]
                    elif return_type == "both":
                        result_data["content"] = full_memory_item["content"]
                        result_data["summary"] = summary_item["summary_text"]

                    memory_items.append(result_data)
            else:
                print(f"Warning: Summary ID {summary_id} not found in SQLite.")

        return memory_items if memory_items else [
            format_response(success=True, message="No matching memories found")
        ]

    except Exception as e:
        return [format_response(
            success=False,
            message=f"Error retrieving from memory: {str(e)}"
        )]


def update_memory(
        memory_id: str,
        content: Optional[str] = None,
        topic: Optional[str] = None,
        tags: Optional[List[str]] = None
) -> dict:
    """Update an existing memory item.
    
    Args:
        memory_id: ID of the memory item to update.
        content: New content (if updating content).
        topic: New topic (if changing).
        tags: New tags (if updating).
        
    Returns:
        dict: Status and updated memory details
    """
    if not any([content, topic, tags]):
        return format_response(
            success=False,
            message="At least one of content, topic, or tags must be provided"
        )

    try:
        # Get current memory item
        current_item = sqlite_manager.get_memory(memory_id)

        if not current_item:
            return format_response(
                success=False,
                message=f"Memory item with ID {memory_id} not found"
            )

        # Update in SQLite
        sqlite_success = sqlite_manager.update_memory(
            memory_id=memory_id,
            content=content,
            topic=topic,
            tags=tags
        )

        # Get updated item for ChromaDB update
        updated_item = sqlite_manager.get_memory(memory_id)

        # Update in ChromaDB
        chroma_success = chroma_manager.update_memory(
            memory_id=memory_id,
            content=updated_item["content"],
            topic=updated_item["topic"],
            tags=updated_item["tags"],
            created_at=updated_item["created_at"]
        )

        # Update topic in ChromaDB if topic changed
        if topic is not None:
            chroma_manager.update_topic(topic, updated_item["tags"])

        # New: Regenerate and update summary if content changed
        summary_updated = False
        if content is not None:
            generated_summary = summarizer.generate_summary(updated_item["content"], summary_type="abstractive",
                                                            length="medium")
            if generated_summary:
                # Assuming there's only one default summary type for now
                existing_summary = sqlite_manager.get_summary(memory_id, "abstractive_medium")
                if existing_summary:
                    summary_updated = sqlite_manager.update_summary(existing_summary["id"], generated_summary)
                    chroma_manager.store_summary_embedding(  # Re-store to update embedding
                        existing_summary["id"],
                        generated_summary,
                        {"memory_id": memory_id, "summary_type": "abstractive_medium", "topic": updated_item["topic"]}
                    )
                else:
                    # If no existing summary, create one (e.g., if content was added before summarization feature)
                    print(f"Creating new summary for memory_id {memory_id} after content update.")
                    summary_id = create_memory_id()
                    summary_updated = sqlite_manager.store_summary(summary_id, memory_id, "abstractive_medium",
                                                                   generated_summary)
                    chroma_manager.store_summary_embedding(
                        summary_id,
                        generated_summary,
                        {"memory_id": memory_id, "summary_type": "abstractive_medium", "topic": updated_item["topic"]}
                    )
            else:
                print(f"Warning: Failed to regenerate summary for memory_id {memory_id} during update.")

        if sqlite_success and chroma_success:
            return format_response(
                success=True,
                message="Memory item updated successfully",
                data={
                    "memory_id": memory_id,
                    "updated_fields": {
                        "content": content is not None,
                        "topic": topic is not None,
                        "tags": tags is not None
                    },
                    "timestamp": timestamp(),
                    "summary_updated": summary_updated
                }
            )
        else:
            return format_response(
                success=False,
                message="Error updating memory item",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success,
                    "summary_updated": summary_updated
                }
            )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error updating memory item: {str(e)}"
        )


def delete_memory(
        memory_id: str
) -> dict:
    """Delete a memory item from the system.

    Args:
        memory_id: ID of the memory item to delete.

    Returns:
        dict: Status of the deletion operation.
    """
    try:
        sqlite_success = sqlite_manager.delete_memory(memory_id)
        chroma_success = chroma_manager.delete_memory(memory_id)

        # New: Delete associated summaries
        sqlite_summary_delete_success = sqlite_manager.delete_summaries(memory_id)

        default_summary = sqlite_manager.get_summary(memory_id, "abstractive_medium")
        chroma_summary_delete_success = True
        if default_summary:
            chroma_summary_delete_success = chroma_manager.delete_summary_embeddings(default_summary["id"])

        if sqlite_success and chroma_success and sqlite_summary_delete_success and chroma_summary_delete_success:
            return format_response(
                success=True,
                message=f"Memory item {memory_id} and its summaries deleted successfully"
            )
        else:
            return format_response(
                success=False,
                message=f"Error deleting memory item {memory_id} or its summaries",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success,
                    "sqlite_summary_delete_success": sqlite_summary_delete_success,
                    "chroma_summary_delete_success": chroma_summary_delete_success
                }
            )
    except Exception as e:
        return format_response(
            success=False,
            message=f"Error deleting memory item: {str(e)}"
        )
