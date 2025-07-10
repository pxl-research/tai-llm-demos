# MCP Server for Persistent Memory

A Model Context Protocol (MCP) server that provides persistent memory capabilities for Large Language Models (LLMs) through a hybrid database architecture.

## Introduction

The MCP Memory Server enables LLMs to store, retrieve, and manage information across conversations and sessions. It serves as an external memory system that allows models to:

- Store important information for later retrieval.
- Search for relevant context using semantic (meaning-based) queries.
- Organize knowledge by topics and tags.
- Track and update information over time.
- Generate summaries of stored knowledge.

This implementation uses a hybrid dual-database architecture:

- **ChromaDB**: Vector database for semantic search capabilities, storing embeddings for both full content and summaries.
- **SQLite**: Relational database for structured data storage and relationships, including full content and various summaries.

## Technologies Used

- **Programming Language**: Python 3.9+
- **Frameworks and Libraries**:
  - `FastMCP`: For implementing the MCP protocol.
  - `ChromaDB`: For vector-based semantic search.
  - `SQLite`: For relational data storage.
  - `python-dotenv`: For environment variable management.
  - `sentence-transformers`: For embedding generation.
  - `pydantic`: For data validation.

## Installation

### Prerequisites

- Python 3.9+
- pip or uv package manager

### Setup

1. Clone or download this repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
# or with uv
uv pip install -r requirements.txt
```

3. Configure environment variables:
   Create a `.env` file in the same directory with the following settings:

```
DB_PATH=/path/to/memory/database
OPENROUTER_API_KEY=sk-or-v1-your_api_key_here
```

If no DB_PATH is specified, the databases will be created in `./memory_db` by default.
The OPENROUTER_API_KEY is required for the summarization functionality.

## Getting Started

### Starting the Server

Run the following command to start the MCP Memory Server:

```bash
python memory_server.py
```

The server will initialize the databases and expose tools for memory operations via the MCP protocol.

## Usage

1. **Initialization**: The server initializes databases at startup.
2. **Memory Operations**:
   - Store new memories with topics and tags.
   - Retrieve memories via semantic search.
   - Update or delete stored content as needed.
3. **Summarization**:
   - Automatic summary generation on memory storage.
   - On-demand summarization with customizable types and lengths.

## API Overview

The MCP Memory Server exposes the following tools:

- `memory_initialize(reset: bool)`: Initialize or reset the memory databases.
- `memory_store(content: str, topic: str, tags: List[str])`: Store new information.
- `memory_retrieve(query: str, max_results: int, topic: str, return_type: str)`: Retrieve information via semantic search.
- `memory_update(memory_id: str, content: str, topic: str, tags: List[str])`: Update existing memory.
- `memory_delete(memory_id: str)`: Delete a memory item.
- `memory_list_topics()`: List all available topics with statistics.
- `memory_status()`: Get system-wide status and statistics.
- `memory_delete_empty_topic(topic_name: str)`: Remove empty topics.
- `memory_summarize(memory_id: str, query: str, topic: str, summary_type: str, length: str)`: Generate summaries.

## Additional Information

For more technical details, refer to the `background_info.md` file in the project directory.
