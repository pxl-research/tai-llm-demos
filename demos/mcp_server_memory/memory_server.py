"""
MCP Server for Persistent Memory.

This server provides a set of tools for storing, retrieving, and managing
persistent memory for LLMs through the Model Context Protocol (MCP).
"""

from typing import List, Optional, Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from config import DB_PATH, OPENROUTER_API_KEY
from db import SQLiteManager, ChromaManager
from utils import create_memory_id, timestamp, format_response
from utils.summarizer import Summarizer # New: Import Summarizer

# Initialize the MCP server
mcp = FastMCP("memory_server")

# Initialize database managers
sqlite_manager = SQLiteManager()
chroma_manager = ChromaManager()

# Initialize summarizer
summarizer = Summarizer(api_key=OPENROUTER_API_KEY) # New: Initialize Summarizer


@mcp.tool()
def memory_initialize(
        reset: Annotated[
            bool,
            Field(
                description="Whether to reset existing memory",
                default=False,
                examples=[False, True]
            )
        ] = False
) -> dict:
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


@mcp.tool()
def memory_store(
        content: Annotated[
            str,
            Field(
                description="The content to store in memory",
                examples=["Quantum computing uses qubits which can exist in multiple states simultaneously."]
            )
        ],
        topic: Annotated[
            str,
            Field(
                description="Primary topic/category for this content",
                examples=["quantum_computing", "machine_learning", "history"]
            )
        ],
        tags: Annotated[
            List[str],
            Field(
                description="Optional tags for better retrieval",
                default=[],
                examples=[["physics", "computing", "technology"], ["ai", "neural_networks"]]
            )
        ] = []
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

        # New: Generate and store summary
        summary_id = create_memory_id()
        generated_summary = summarizer.generate_summary(content, summary_type="abstractive", length="medium")

        summary_stored = False
        if generated_summary:
            summary_stored = sqlite_manager.store_summary(summary_id, memory_id, "abstractive_medium", generated_summary)
            chroma_manager.store_summary_embedding(
                summary_id,
                generated_summary,
                {"memory_id": memory_id, "summary_type": "abstractive_medium", "topic": topic}
            )
        else:
            print(f"Warning: Failed to generate summary for memory_id {memory_id}. Original content stored without summary.")

        if sqlite_success and chroma_success:
            return format_response(
                success=True,
                message="Content stored successfully",
                data={
                    "memory_id": memory_id,
                    "topic": topic,
                    "tags": tags,
                    "timestamp": now,
                    "summary_generated": bool(generated_summary), # New: Indicate if summary was generated
                    "summary_stored": summary_stored # New: Indicate if summary was stored
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
                    "summary_generated": bool(generated_summary), # New: Indicate if summary was generated
                    "summary_stored": summary_stored # New: Indicate if summary was stored
                }
            )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error storing content: {str(e)}"
        )


@mcp.tool()
def memory_retrieve(
        query: Annotated[
            str,
            Field(
                description="The query to search for in memory",
                examples=["How do quantum computers work?", "Tell me about machine learning"]
            )
        ],
        max_results: Annotated[
            int,
            Field(
                description="Maximum number of results to return",
                default=5,
                examples=[3, 5, 10]
            )
        ] = 5,
        topic: Annotated[
            Optional[str],
            Field(
                description="Optional topic to restrict search to",
                default=None,
                examples=["quantum_computing", "machine_learning"]
            )
        ] = None,
        return_type: Annotated[
            Literal["full_text", "summary", "both"],
            Field(
                description="The type of content to return: full_text, summary, or both",
                default="full_text",
                examples=["full_text", "summary", "both"]
            )
        ] = "full_text"
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
            summary_item = sqlite_manager.get_summary_by_id(summary_id) # Assuming a new method to get summary by its own ID
            if summary_item:
                memory_id = summary_item["memory_id"]
                full_memory_item = sqlite_manager.get_memory(memory_id)
                
                if full_memory_item:
                    result_data = {
                        "id": memory_id,
                        "topic": full_memory_item["topic"],
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

        return memory_items if memory_items else [
            format_response(success=True, message="No matching memories found")
        ]

    except Exception as e:
        return [format_response(
            success=False,
            message=f"Error retrieving from memory: {str(e)}"
        )]


@mcp.tool()
def memory_update(
        memory_id: Annotated[
            str,
            Field(
                description="ID of the memory item to update",
                examples=["550e8400-e29b-41d4-a716-446655440000"]
            )
        ],
        content: Annotated[
            Optional[str],
            Field(
                description="New content (if updating content)",
                default=None,
                examples=["Updated information about quantum computing"]
            )
        ] = None,
        topic: Annotated[
            Optional[str],
            Field(
                description="New topic (if changing)",
                default=None,
                examples=["quantum_physics"]
            )
        ] = None,
        tags: Annotated[
            Optional[List[str]],
            Field(
                description="New tags (if updating)",
                default=None,
                examples=[["updated", "revised", "quantum"]]
            )
        ] = None
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
            generated_summary = summarizer.generate_summary(updated_item["content"], summary_type="abstractive", length="medium")
            if generated_summary:
                # Assuming there's only one default summary type for now
                existing_summary = sqlite_manager.get_summary(memory_id, "abstractive_medium")
                if existing_summary:
                    summary_updated = sqlite_manager.update_summary(existing_summary["id"], generated_summary)
                    chroma_manager.store_summary_embedding( # Re-store to update embedding
                        existing_summary["id"],
                        generated_summary,
                        {"memory_id": memory_id, "summary_type": "abstractive_medium", "topic": updated_item["topic"]}
                    )
                else:
                    # If no existing summary, create one (e.g., if content was added before summarization feature)
                    summary_id = create_memory_id()
                    summary_updated = sqlite_manager.store_summary(summary_id, memory_id, "abstractive_medium", generated_summary)
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
                    "summary_updated": summary_updated # New: Indicate if summary was updated
                }
            )
        else:
            return format_response(
                success=False,
                message="Error updating memory item",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success,
                    "summary_updated": summary_updated # New: Indicate if summary was updated
                }
            )

    except Exception as e:
        return format_response(
            success=False,
            message=f"Error updating memory item: {str(e)}"
        )


@mcp.tool()
def memory_list_topics() -> List[dict]:
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


@mcp.tool()
def memory_status() -> dict:
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


@mcp.tool()
def memory_delete(
        memory_id: Annotated[
            str,
            Field(
                description="ID of the memory item to delete",
                examples=["550e8400-e29b-41d4-a716-446655440000"]
            )
        ]
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
        # Note: ChromaDB delete_summary_embeddings takes summary_id, not memory_id.
        # We would need to retrieve summary_ids first or modify delete_summary_embeddings
        # to handle memory_id for bulk deletion. For now, we'll assume a single default summary.
        # A more robust solution would involve iterating through all summaries for a memory_id.
        # For simplicity, assuming we only delete the default 'abstractive_medium' summary for now.
        # In a real scenario, we'd fetch all summary_ids for this memory_id from SQLite first.
        
        # For now, let's assume we need to fetch the summary_id from SQLite first
        # This part needs a more robust implementation if multiple summaries per memory_id are expected
        # For simplicity, we'll just try to delete the default summary embedding if it exists
        default_summary = sqlite_manager.get_summary(memory_id, "abstractive_medium")
        chroma_summary_delete_success = True # Assume success if no default summary or deletion works
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


@mcp.tool()
def memory_summarize(
        memory_id: Annotated[
            Optional[str],
            Field(
                description="ID of the memory item to summarize",
                examples=["550e8400-e29b-41d4-a716-446655440000"]
            )
        ] = None,
        query: Annotated[
            Optional[str],
            Field(
                description="A query to find relevant memories to summarize",
                examples=["key points of quantum computing"]
            )
        ] = None,
        topic: Annotated[
            Optional[str],
            Field(
                description="A topic to find relevant memories to summarize",
                examples=["quantum_computing"]
            )
        ] = None,
        summary_type: Annotated[
            Literal["abstractive", "extractive", "query_focused"],
            Field(
                description="The type of summary to generate",
                default="abstractive",
                examples=["abstractive", "extractive", "query_focused"]
            )
        ] = "abstractive",
        length: Annotated[
            Literal["short", "medium", "detailed"],
            Field(
                description="The desired length of the summary",
                default="medium",
                examples=["short", "medium", "detailed"]
            )
        ] = "medium"
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


if __name__ == "__main__":
    print('Initializing memory server...')

    # Initialize the memory system on startup
    init_result = memory_initialize()
    print(f"Initialization result: {init_result['status']}")

    # Run the MCP server
    mcp.run(transport='stdio')
