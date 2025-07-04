# Technical Documentation: MCP Server Memory

## Project Overview

The MCP Server Memory is a Model Context Protocol (MCP) server implementation that provides persistent memory capabilities for Large Language Models (LLMs). It allows LLMs to store, retrieve, and manage information across conversations and sessions through a hybrid database architecture.

## Architecture

### Core Components

1. **`memory_server.py`**: The main server application that implements the MCP protocol and exposes memory-related tools to clients.
   - Initializes the MCP server using FastMCP
   - Defines and registers MCP tools for memory operations
   - Handles the server startup and communication via stdio

2. **`memory_service/`**: Contains the core business logic for memory operations
   - `core_memory_service.py`: Implements primary memory operations (initialize, store, retrieve, update, delete)
   - `auxiliary_memory_service.py`: Implements secondary operations (listing topics, getting status, summarization)

3. **`db/`**: Database management components
   - SQLite Manager: Handles structured storage of memory items, summaries, and metadata
   - ChromaDB Manager: Handles vector embeddings for semantic search capabilities

4. **`utils/`**: Utility functions and helper modules
   - ID generation, timestamp creation, response formatting
   - Summarizer: Generates abstractive summaries of stored content

### Database Architecture

The project uses a hybrid dual-database approach:

1. **SQLite**: Relational database for structured data storage
   - Memory items with full content
   - Metadata (topics, tags, timestamps)
   - Summaries of various types and lengths

2. **ChromaDB**: Vector database for semantic search
   - Stores embeddings of both full content and summaries
   - Enables semantic search based on meaning rather than keywords
   - Organizes content by topics and tags

## API Reference

The MCP Server exposes the following tools via the Model Context Protocol:

### Core Tools
- `memory_initialize(reset: bool)`: Initialize or reset the memory databases
- `memory_store(content: str, topic: str, tags: List[str])`: Store new information
- `memory_retrieve(query: str, max_results: int, topic: str, return_type: str)`: Retrieve information via semantic search
- `memory_update(memory_id: str, content: str, topic: str, tags: List[str])`: Update existing memory
- `memory_delete(memory_id: str)`: Delete a memory item

### Auxiliary Tools
- `memory_list_topics()`: List all available topics with statistics
- `memory_status()`: Get system-wide status and statistics
- `memory_delete_empty_topic(topic_name: str)`: Remove empty topics
- `memory_summarize(memory_id: str, query: str, topic: str, summary_type: str, length: str)`: Generate summaries

## Configuration

Configuration is managed through `config.py` and environment variables:

- **Database Paths**:
  - `DB_PATH`: Base directory for databases (default: "./memory_db")
  - `SQLITE_PATH`: Path to SQLite database
  - `CHROMA_PATH`: Path to ChromaDB database

- **OpenRouter API Settings**:
  - `OPENROUTER_API_KEY`: Required for summary generation
  - `OPENROUTER_ENDPOINT`: API endpoint URL

## Usage Flow

1. **Initialization**: Server initializes databases at startup
2. **Memory Operations**:
   - Client applications connect via MCP
   - Clients can store new memories with topics and tags
   - Memories can be retrieved via semantic search
   - Content can be updated or deleted as needed
3. **Summarization**:
   - Automatic summary generation on memory storage
   - On-demand summarization with different types (abstractive, extractive, query-focused)
   - Customizable summary length (short, medium, detailed)

## Dependencies

- FastMCP: For Model Context Protocol implementation
- SQLite: For relational database storage
- ChromaDB: For vector database and semantic search
- Pydantic: For data validation and settings management
- OpenRouter: For generating summaries and other LLM operations
