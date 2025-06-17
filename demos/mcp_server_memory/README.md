# MCP Server for Persistent Memory

A Model Context Protocol (MCP) server that provides persistent memory capabilities for Large Language Models (LLMs) through a hybrid database architecture.

## Introduction

The MCP Memory Server enables LLMs to store, retrieve, and manage information across conversations and sessions. It serves as an external memory system that allows models to:

- Store important information for later retrieval
- Search for relevant context using semantic (meaning-based) queries
- Organize knowledge by topics and tags
- Track and update information over time

This implementation uses a hybrid dual-database architecture:

- **ChromaDB**: Vector database for semantic search capabilities
- **SQLite**: Relational database for structured data storage and relationships

## Installation

### Prerequisites

- Python 3.9+
- pip or uv package manager

### Setup

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
# or with uv
uv pip install -r requirements.txt
```

3. Configure environment variables (optional):
   Create a `.env` file in the same directory with the following settings:

```
DB_PATH=/path/to/memory/database
```

If no path is specified, the databases will be created in `./memory_db` by default.

## Getting Started

### Starting the Server

Run the server using:

```bash
python memory_server.py
```

The server will initialize the databases on startup and begin listening for MCP requests on standard I/O.

### Example Usage

Here's a basic example of how to use the MCP Memory Server from a client:

```python
from mcp.client import Client

# Connect to the memory server
client = Client(transport="stdio", command=["python", "memory_server.py"])

# Store information
response = client.invoke("memory_store", {
    "content": "Quantum computing uses qubits which can exist in multiple states simultaneously.",
    "topic": "quantum_computing",
    "tags": ["physics", "computing", "technology"]
})
memory_id = response["memory_id"]

# Retrieve information by semantic search
results = client.invoke("memory_retrieve", {
    "query": "How do quantum computers work?",
    "max_results": 3
})

# View all available topics
topics = client.invoke("memory_list_topics", {})

# Update existing information
client.invoke("memory_update", {
    "memory_id": memory_id,
    "content": "Updated information about quantum computing"
})

# Check system status
status = client.invoke("memory_status", {})
```

## API Reference

The server provides the following MCP tools:

### `memory_initialize`

Initializes or resets the memory system databases.

**Parameters:**
- `reset` (bool, optional): Whether to reset existing memory. Default: False

**Returns:**
- Status and initialization information

### `memory_store`

Stores new information in the persistent memory system.

**Parameters:**
- `content` (str): The text content to store in memory
- `topic` (str): Primary topic/category for this content
- `tags` (List[str], optional): Optional tags for better retrieval. Default: []

**Returns:**
- Status and ID of the stored content

### `memory_retrieve`

Retrieves information from memory using semantic search.

**Parameters:**
- `query` (str): The search query to find relevant information
- `max_results` (int, optional): Maximum number of results to return. Default: 5
- `topic` (str, optional): Optional topic to restrict search to. Default: None

**Returns:**
- List of matching memory items with content and metadata

### `memory_update`

Updates an existing memory item.

**Parameters:**
- `memory_id` (str): ID of the memory item to update
- `content` (str, optional): New content (if updating content). Default: None
- `topic` (str, optional): New topic (if changing). Default: None
- `tags` (List[str], optional): New tags (if updating). Default: None

**Returns:**
- Status and updated memory details

### `memory_list_topics`

Lists all available topics/knowledge domains in the memory system.

**Parameters:**
- None

**Returns:**
- List of available topics with counts and descriptions

### `memory_status`

Gets memory system status and statistics.

**Parameters:**
- None

**Returns:**
- Statistics about memory usage, counts, etc.

## Architecture Overview

### Dual-Database System

The MCP Memory Server uses a hybrid architecture that combines the strengths of two database systems:

1. **ChromaDB (Vector Database)**
   - Stores text embeddings for semantic search
   - Handles similarity-based queries
   - Manages metadata for quick filtering

2. **SQLite (Relational Database)**
   - Stores full content and relationships
   - Handles structured data and queries
   - Manages versioning and update history

### Data Flow

#### Storage Process
1. Content is received via the `memory_store` method
2. A unique ID is generated for the memory item
3. Content and metadata are stored in SQLite
4. Text is embedded and stored in ChromaDB with reference to the SQLite record
5. Topic information is updated in both databases

#### Retrieval Process
1. Query is received via the `memory_retrieve` method
2. ChromaDB performs semantic search to find relevant memory IDs
3. Full content is fetched from SQLite using the IDs
4. Results are returned to the client

## Advanced Usage

### Organizing with Topics and Tags

For optimal retrieval, consider how to organize your memory:

- **Topics**: Use for broad categories (e.g., "quantum_computing", "history")
- **Tags**: Use for specific attributes or cross-cutting concerns

Example organization:
```
Topic: "machine_learning"
Tags: ["neural_networks", "supervised", "classification"]

Topic: "history"
Tags: ["world_war_2", "europe", "1940s"]
```

### Performance Considerations

- Store related information together for better retrieval
- Use specific topics and descriptive tags
- Consider the length of stored content (shorter is often better for embeddings)
- Reset the database periodically if it grows too large and performance degrades

## Troubleshooting

### Common Issues

- **Database Connection Errors**: Ensure the DB_PATH directory is writable
- **Memory Not Found**: Check that the memory_id exists and is correct
- **ChromaDB Errors**: May require reinstalling sentence-transformers

### Logging

The server outputs basic status information to the console. For more detailed logging, consider modifying the code to use Python's logging module.

## Development and Contribution

### Project Structure

```
mcp_server_memory/
├── memory_server.py       # Main MCP server with tool definitions
├── config.py              # Configuration settings
├── db/
│   ├── __init__.py        # Database module exports
│   ├── sqlite_manager.py  # SQLite database operations
│   └── chroma_manager.py  # ChromaDB operations
└── utils/
    ├── __init__.py        # Utility module exports
    └── helpers.py         # Helper functions
```

### Extending the Server

To add new capabilities:

1. Create a new method in the appropriate manager class
2. Add a new tool method in `memory_server.py`
3. Decorate it with `@mcp.tool()`
4. Document parameters using Annotated and Field

## License

This project is provided as open source software.

## Acknowledgements

- Built with the Model Context Protocol (MCP) framework
- Uses ChromaDB for vector search capabilities
- Inspired by the need for persistent memory in LLM applications
