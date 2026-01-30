# Advanced LLM Chat Application

A comprehensive NiceGui-based chat application featuring LLM integration, document RAG, tool calling, and conversation persistence.

## Features

### Phase 1: Core Chat UI (✓ Implemented)
- Real-time chat interface with streaming responses
- Clean, modern NiceGui UI
- Message history tracking
- System instruction support

### Phase 2: Persistence & Authentication (✓ Implemented)
- User authentication via `.passwd` file
- Conversation history persistence (JSON-based)
- Save/load conversations
- Per-user conversation storage

### Phase 3: Model Selection & Settings (✓ Implemented)
- Dynamic model selection from OpenRouter
- Display model metadata (pricing, context length, capabilities)
- Temperature adjustment
- Live model switching during chat

### Phase 4: Tools & Tool Calling (✓ Implemented)
- **Web Search**: Google Custom Search integration
- **Web Scraper**: Extract content from webpages
- **RAG Lookup**: Search uploaded documents
- Token-aware tool orchestration
- Automatic tool result integration

### Phase 5: Document Upload & RAG (✓ Implemented)
- File upload for documents (PDF, DOCX, PPTX, XLSX, XLS)
- Automatic document conversion to markdown
- ChromaDB-based vector embedding and retrieval
- Document management (add/remove)
- Context-aware RAG integration with chat

### Phase 6: MCP Integration (Optional)
- Ready for MCP client implementation
- Extensible tool registration system

## Installation

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
cd applications/advanced_chat
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENROUTER_API_KEY (required)
# - GOOGLE_API_KEY (for web search)
# - GOOGLE_SEARCH_ENGINE_ID (for web search)
# - DEFAULT_MODEL (optional, defaults to claude-haiku-4.5)
```

### 4. Set Up Default User
```bash
python3 -c "from utils.auth import register_user; register_user('test', 'test')"
```

Or use the existing test user: `username: test`, `password: test`

## Usage

### Start the Application
```bash
python3 launch_ui.py
```

The application will be available at `http://127.0.0.1:7860`

### Login
- Default credentials: `test` / `test`
- Custom credentials require `.passwd` file entries

### Chat
1. Enter your message in the input field
2. LLM responds with streaming output
3. Tools are automatically called when relevant
4. Documents can be uploaded for RAG context

### Model Selection
- Click the ⚙️ settings icon
- Switch to "Model Selection" tab
- Click "Load Available Models"
- Select desired model and temperature
- Changes apply immediately

### Document Management
- **Upload**: Drag and drop or click to upload documents
- **Delete**: Click delete icon next to document name
- **Query**: Type questions that reference uploaded content
- RAG automatically includes relevant context in responses

### Conversation History
- Click "Load Recent" to view saved conversations
- Conversations auto-save in `data/users/<username>/conversations/`
- Msgpack binary format for efficient storage

## Architecture

### Services Layer
- **LLMService**: OpenRouter client wrapper with model management
- **HistoryService**: Conversation persistence and management
- **ToolService**: Tool registration and orchestration
- **RAGService**: Document indexing and retrieval via ChromaDB

### Components Layer
- **ChatInterface**: Message display and user input handling
- **SettingsModal**: Model and settings configuration
- **DocumentPanel**: File upload and document management

### Tools
- **web_search.py**: Google Custom Search integration
- **web_scraper.py**: Web content extraction
- **rag_lookup.py**: Document search and retrieval

### Configuration
- **config.py**: Centralized configuration and paths
- **auth.py**: Authentication wrapper (reuses `components/auth/`)

## Data Storage

### Directory Structure
```
applications/advanced_chat/
├── data/
│   └── users/             # Per-user data directories
│       └── {username}/    # Each user has their own folder
│           ├── conversations/  # User's chat histories (msgpack)
│           ├── rag_db/        # User's ChromaDB vector store
│           └── settings.json  # User's model/temperature preferences
├── .passwd                # User credentials (bcrypt hashed)
└── .env                   # Environment variables
```

### Conversation Format
Msgpack binary files in `data/users/{username}/conversations/`:
```python
{
  "conversation_id": "uuid-...",
  "user": "username",
  "created_at": "2025-01-21T12:00:00Z",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "model": "anthropic/claude-haiku-4.5",
  "settings": {"temperature": 0.7}
}
```
Note: Files are stored in msgpack binary format for efficiency, but the data structure remains the same.

## API Keys Required

### OpenRouter (Required)
1. Sign up at https://openrouter.ai
2. Get your API key from dashboard
3. Add to `.env`: `OPENROUTER_API_KEY=your_key`

### Google Search (Optional, for web search tool)
1. Create Google Custom Search Engine: https://cse.google.com
2. Get API key from Google Cloud Console
3. Add to `.env`:
   - `GOOGLE_API_KEY=your_key`
   - `GOOGLE_SEARCH_ENGINE_ID=your_cse_id`

## Development Notes

### Extending Tools
To add a new tool:

1. Create tool file in `tools/` directory:
```python
def my_tool(param: str) -> dict:
    """Tool implementation."""
    return {"result": "..."}

my_tool_descriptor = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "...",
        "parameters": {...}
    }
}
```

2. Register in `launch_ui.py`:
```python
from tools.my_tool import my_tool, my_tool_descriptor

tool_service.register_tool('my_tool', my_tool, my_tool_descriptor)
```

### Adding Models
Models are dynamically fetched from OpenRouter. The settings UI shows:
- All available models
- Pricing information
- Context length
- Max completion tokens

### Document Format Support
Powered by `markitdown`, supports:
- PDF documents
- Microsoft Office (DOCX, PPTX, XLSX, XLS)
- Automatic markdown conversion
- Semantic chunking for RAG

## Troubleshooting

### Models not loading
- Check OpenRouter API key is valid
- Verify internet connection
- Models are cached; try refreshing the page

### Documents not indexing
- Ensure file format is supported
- Check file size (markitdown has limits)
- Verify write permissions in `data/rag_db/`

### Authentication issues
- Ensure `.passwd` file exists
- Default user: `test/test`
- Register new users via `utils/auth.register_user()`

### Tool failures
- Check environment variables (Google API keys)
- Verify rate limits aren't exceeded
- Tool errors are logged and displayed in chat

## Future Enhancements

### Phase 6: MCP Integration (Optional/v2)
- MCP client connection
- Discovery of MCP tools
- Server lifecycle management
- Support for Slack, file I/O, and custom MCP servers

### Planned Improvements
- Voice input/output
- Image support in chat
- Conversation search/tagging
- Import/export conversations
- Multiple conversation threading
- Rate limiting and usage tracking
- Batch operations for documents
- Custom system instructions per conversation

## Performance Considerations

### Streaming
- Responses stream in real-time
- Large documents processed asynchronously
- RAG queries optimized to top-5 results

### Storage
- Conversations stored as msgpack (binary format for efficiency)
- RAG DB persisted in ChromaDB per user
- User settings stored as JSON (model, temperature)
- Complete per-user data isolation in `data/users/{username}/`

### API Rate Limits
- OpenRouter: Check https://openrouter.ai for limits
- Google Search: 100 queries/day (free tier)
- Consider caching for heavy usage

## License & Attribution

This application builds upon the `tai-llm-demos` repository components:
- `components/open_router/`: LLM client and model filtering
- `components/auth/`: User authentication
- `components/text_utils/`: Document conversion
- `components/vectorstore/`: ChromaDB wrapper

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review configuration in `utils/config.py`
3. Check logs and error messages in console
4. Refer to parent repository: https://github.com/pxl-research/tai-llm-demos
