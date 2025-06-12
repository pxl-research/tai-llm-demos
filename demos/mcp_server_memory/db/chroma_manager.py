"""
ChromaDB manager for the MCP Memory Server.
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional, Union

from ..config import CHROMA_PATH, MEMORY_COLLECTION, TOPICS_COLLECTION
from ..utils import timestamp

class ChromaManager:
    """Manager for ChromaDB operations."""
    
    def __init__(self):
        """Initialize the ChromaDB manager."""
        self._ensure_dir_exists()
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction()
        self.client = self._get_client()
        
    def _ensure_dir_exists(self):
        """Ensure the database directory exists."""
        os.makedirs(CHROMA_PATH, exist_ok=True)
    
    def _get_client(self):
        """Get a ChromaDB client.
        
        Returns:
            chromadb.PersistentClient: A ChromaDB client
        """
        return chromadb.PersistentClient(path=CHROMA_PATH)
    
    def initialize(self, reset: bool = False) -> bool:
        """Initialize the ChromaDB database.
        
        Args:
            reset: Whether to reset the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if reset:
                try:
                    self.client.reset()
                    # Re-initialize the client after reset
                    self.client = self._get_client()
                except Exception as e:
                    print(f"Warning during ChromaDB reset: {e}")
            
            # Create collections
            self.client.get_or_create_collection(
                name=MEMORY_COLLECTION,
                embedding_function=self.embedding_function
            )
            
            self.client.get_or_create_collection(
                name=TOPICS_COLLECTION,
                embedding_function=self.embedding_function
            )
            
            return True
        
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            return False
    
    def store_memory(self, memory_id: str, content: str, topic: str, tags: List[str]) -> bool:
        """Store a memory item in ChromaDB.
        
        Args:
            memory_id: Unique ID for the memory item
            content: The content to store
            topic: The topic category
            tags: List of tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            collection = self.client.get_collection(MEMORY_COLLECTION)
            
            collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[{
                    "id": memory_id,
                    "topic": topic,
                    "tags": tags,
                    "created_at": now,
                    "updated_at": now
                }]
            )
            
            return True
        
        except Exception as e:
            print(f"Error storing memory in ChromaDB: {e}")
            return False
    
    def update_topic(self, topic: str, tags: Optional[List[str]] = None) -> bool:
        """Update or create a topic in ChromaDB.
        
        Args:
            topic: The topic name
            tags: Associated tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            topic_collection = self.client.get_collection(TOPICS_COLLECTION)
            topic_summary = f"Topic {topic} containing information about {', '.join(tags) if tags else topic}"
            
            try:
                # Check if topic exists
                topic_collection.get(ids=[topic])
                # Topic exists, update it
                topic_collection.update(
                    ids=[topic],
                    documents=[topic_summary],
                    metadatas=[{
                        "name": topic,
                        "updated_at": now
                    }]
                )
            except Exception:
                # Topic doesn't exist, add it
                topic_collection.add(
                    ids=[topic],
                    documents=[topic_summary],
                    metadatas=[{
                        "name": topic,
                        "created_at": now
                    }]
                )
            
            return True
        
        except Exception as e:
            print(f"Error updating topic in ChromaDB: {e}")
            return False
    
    def search_memories(self, query: str, max_results: int = 5, 
                       topic: Optional[str] = None) -> List[str]:
        """Search for memories using semantic search.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            topic: Optional topic to restrict search to
            
        Returns:
            List[str]: List of memory IDs matching the query
        """
        try:
            collection = self.client.get_collection(MEMORY_COLLECTION)
            
            # Prepare filter if topic is specified
            where_filter = {"topic": topic} if topic else None
            
            # Perform semantic search
            results = collection.query(
                query_texts=[query],
                n_results=max_results,
                where=where_filter
            )
            
            # Extract memory IDs
            memory_ids = []
            if results and len(results["ids"]) > 0 and len(results["ids"][0]) > 0:
                memory_ids = results["ids"][0]
                
            return memory_ids
        
        except Exception as e:
            print(f"Error searching memories in ChromaDB: {e}")
            return []
    
    def update_memory(self, memory_id: str, content: str, topic: str, 
                     tags: List[str], created_at: str) -> bool:
        """Update a memory item in ChromaDB.
        
        Args:
            memory_id: The ID of the memory to update
            content: The updated content
            topic: The updated topic
            tags: The updated tags
            created_at: The original creation timestamp
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            collection = self.client.get_collection(MEMORY_COLLECTION)
            
            collection.update(
                ids=[memory_id],
                documents=[content],
                metadatas=[{
                    "id": memory_id,
                    "topic": topic,
                    "tags": tags,
                    "created_at": created_at,
                    "updated_at": now
                }]
            )
            
            return True
        
        except Exception as e:
            print(f"Error updating memory in ChromaDB: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get ChromaDB status information.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            return {
                "chroma_collection_count": len(self.client.list_collections()),
                "chroma_path": CHROMA_PATH
            }
        
        except Exception as e:
            print(f"Error getting ChromaDB status: {e}")
            return {}
