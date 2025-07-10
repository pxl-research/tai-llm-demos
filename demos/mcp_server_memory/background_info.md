# Technical Documentation: MCP Server Memory

## Project Overview

The MCP Server Memory is a Model Context Protocol (MCP) server implementation that provides persistent memory capabilities for Large Language Models (LLMs). It allows LLMs to store, retrieve, and manage information across conversations and sessions through a hybrid database architecture.

## Architecture

### Core Components

1. **`memory_server.py`**: The main server application that implements the MCP protocol and exposes memory-related tools to clients.
   - Initializes the MCP server using FastMCP.
   - Defines and registers MCP tools for memory operations.
   - Handles the server startup and communication via stdio.

2. **`memory_service/`**: Contains the core business logic for memory operations.
   - `core_memory_service.py`: Implements primary memory operations (initialize, store, retrieve, update, delete).
   - `auxiliary_memory_service.py`: Implements secondary operations (listing topics, getting status, summarization).

3. **`db/`**: Database management components.
   - SQLite Manager: Handles structured storage of memory items, summaries, and metadata.
   - ChromaDB Manager: Handles vector embeddings for semantic search capabilities.

4. **`utils/`**: Utility functions and helper modules.
   - ID generation, timestamp creation, response formatting.
   - Summarizer: Generates abstractive summaries of stored content.

### Database Architecture

The project uses a hybrid dual-database approach:

1. **SQLite**: Relational database for structured data storage.
   - Stores memory items with full content, metadata (topics, tags, timestamps), and summaries.

2. **ChromaDB**: Vector database for semantic search.
   - Stores embeddings of both full content and summaries.
   - Enables semantic search based on meaning rather than keywords.

## API Reference

The MCP Server exposes the following tools via the Model Context Protocol:

### Core Tools
- `memory_initialize(reset: bool)`: Initialize or reset the memory databases.
- `memory_store(content: str, topic: str, tags: List[str])`: Store new information.
- `memory_retrieve(query: str, max_results: int, topic: str, return_type: str)`: Retrieve information via semantic search.
- `memory_update(memory_id: str, content: str, topic: str, tags: List[str])`: Update existing memory.
- `memory_delete(memory_id: str)`: Delete a memory item.

### Auxiliary Tools
- `memory_list_topics()`: List all available topics with statistics.
- `memory_status()`: Get system-wide status and statistics.
- `memory_delete_empty_topic(topic_name: str)`: Remove empty topics.
- `memory_summarize(memory_id: str, query: str, topic: str, summary_type: str, length: str)`: Generate summaries.

## Configuration

### `config.py`

- Loads environment variables using `dotenv`.
- Defines paths for SQLite and ChromaDB databases.
- Configures OpenRouter API settings and other parameters like default maximum results.

## Development Plan

### `development_plan.md`

- Summarizes the project's current status, completed tasks, and future plans.
- Highlights the dual-database architecture and references a high-level architecture diagram.

## Dependencies

### `requirements.txt`

- Lists the following dependencies:
  - `mcp[cli]`
  - `python-dotenv`
  - `chromadb`
  - `sentence-transformers`
  - `pydantic`

## Server Implementation

### `memory_server.py`

- Implements the MCP Memory Server using the `FastMCP` framework.
- Provides tools for initializing and managing memory, such as `memory_initialize` and `memory_store`.
- Imports core and auxiliary memory services for handling operations.

## Usage Flow

1. **Initialization**: Server initializes databases at startup.
2. **Memory Operations**:
   - Client applications connect via MCP.
   - Clients can store new memories with topics and tags.
   - Memories can be retrieved via semantic search.
   - Content can be updated or deleted as needed.
3. **Summarization**:
   - Automatic summary generation on memory storage.
   - On-demand summarization with different types (abstractive, extractive, query-focused).
   - Customizable summary length (short, medium, detailed).

## Memory Service

### `memory_service/`

- **`core_memory_service.py`**: Implements primary memory operations, such as initialize, store, retrieve, update, and delete.
- **`auxiliary_memory_service.py`**: Implements secondary operations, including listing topics, getting status, and summarization.

## Utilities

### `utils/`

- **`helpers.py`**: Provides utility functions for ID generation, timestamp creation, and response formatting.
- **`summarizer.py`**: Implements abstractive summarization of stored content.

## Database Management

### `db/`

- **`chroma_manager.py`**: Manages ChromaDB operations, including embedding storage and semantic search.
- **`sqlite_connection.py`**: Handles SQLite database connections.
- **`sqlite_manager.py`**: Manages SQLite operations, such as storing and retrieving structured data.
