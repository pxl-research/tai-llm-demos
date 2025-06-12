"""
MCP Server for Persistent Memory.

This server provides a set of tools for storing, retrieving, and managing
persistent memory for LLMs through the Model Context Protocol (MCP).
"""

from typing import List, Optional, Dict, Any, Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from db import SQLiteManager, ChromaManager
from utils import create_memory_id, timestamp, format_response
from config import DB_PATH

# Initialize the MCP server
mcp = FastMCP("memory_server")

# Initialize database managers
sqlite_manager = SQLiteManager()
chroma_manager = ChromaManager()

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
        
        if sqlite_success and chroma_success:
            return format_response(
                success=True,
                message="Content stored successfully",
                data={
                    "memory_id": memory_id,
                    "topic": topic,
                    "tags": tags,
                    "timestamp": now
                }
            )
        else:
            return format_response(
                success=False,
                message="Error storing content",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success,
                    "topic_success": topic_success
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
    ] = None
) -> List[dict]:
    """Retrieve information from memory using semantic search.
    
    Args:
        query: The search query to find relevant information.
        max_results: Maximum number of results to return.
        topic: Optional topic to restrict search to.
        
    Returns:
        List[dict]: List of matching memory items with content and metadata
    """
    try:
        # Perform semantic search in ChromaDB
        memory_ids = chroma_manager.search_memories(query, max_results, topic)
        
        # Retrieve full content from SQLite
        memory_items = []
        for memory_id in memory_ids:
            item = sqlite_manager.get_memory(memory_id)
            if item:
                memory_items.append(item)
        
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
                    "timestamp": timestamp()
                }
            )
        else:
            return format_response(
                success=False,
                message="Error updating memory item",
                data={
                    "sqlite_success": sqlite_success,
                    "chroma_success": chroma_success
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

if __name__ == "__main__":
    print('Initializing memory server...')
    
    # Initialize the memory system on startup
    init_result = memory_initialize()
    print(f"Initialization result: {init_result['status']}")
    
    # Run the MCP server
    mcp.run(transport='stdio')
