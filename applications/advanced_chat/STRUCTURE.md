# Project Structure

## Directory Overview

```
applications/advanced_chat/
├── launch_ui.py                    # Main entry point - orchestrates all phases
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── README.md                       # Comprehensive user guide
├── QUICKSTART.md                   # 5-minute setup guide
├── IMPLEMENTATION_SUMMARY.md       # Technical implementation details
├── STRUCTURE.md                    # This file
│
├── components/                     # UI Components
│   ├── __init__.py
│   ├── chat_interface.py          # Phase 1: Chat display & message handling
│   ├── settings_modal.py          # Phase 3: Model selection & settings
│   └── document_panel.py          # Phase 5: Document upload & management
│
├── services/                       # Business Logic Layer
│   ├── __init__.py
│   ├── llm_service.py             # Phase 1: LLM client management
│   ├── history_service.py         # Phase 2: Conversation persistence
│   ├── tool_service.py            # Phase 4: Tool registration & execution
│   └── rag_service.py             # Phase 5: Document indexing & retrieval
│
├── tools/                          # Tool Implementations
│   ├── __init__.py
│   ├── web_search.py              # Phase 4: Google Search tool
│   ├── web_scraper.py             # Phase 4: Web content extraction
│   └── rag_lookup.py              # Phase 5: Document search tools
│
├── utils/                          # Utilities & Configuration
│   ├── __init__.py
│   ├── config.py                  # Centralized configuration
│   └── auth.py                    # Authentication (wraps components/auth/)
│
├── data/                           # Runtime Data (auto-created)
│   ├── conversations/             # User conversation histories (JSON)
│   │   └── {username}/           # Per-user directory
│   │       ├── {conv_id_1}.json
│   │       ├── {conv_id_2}.json
│   │       └── ...
│   └── rag_db/                    # ChromaDB vector store
│
├── .passwd                         # User credentials (auto-created, bcrypt hashed)
├── .env                            # Environment variables (auto-created from .env.example)
└── __pycache__/                    # Python cache (auto-created)
```

## File Descriptions

### Entry Point
- **launch_ui.py** (330 lines)
  - Main application orchestration
  - Integrates all phases (1-5)
  - UI building and NiceGui setup
  - Authentication flow
  - Tool registration and callbacks

### Components (UI Layer)

- **chat_interface.py** (140 lines)
  - NiceGui chatbot widget
  - Message streaming display
  - Input field and send button
  - Message history management
  - Tool call handling (Phase 4)

- **settings_modal.py** (190 lines)
  - Modal dialog for settings
  - Model selection tab
  - Advanced settings (temperature)
  - Dynamic model loading from OpenRouter

- **document_panel.py** (150 lines)
  - File upload widget
  - Document list display
  - Document deletion
  - Upload status feedback

### Services (Business Logic Layer)

- **llm_service.py** (55 lines)
  - OpenRouter client wrapper
  - Model switching
  - Temperature management
  - Tool registration
  - Streaming completion interface

- **history_service.py** (200 lines)
  - Conversation persistence (JSON)
  - Save/load conversations
  - List recent conversations
  - Export conversations (JSON/MD/TXT)
  - Delete conversations
  - Conversation preview with pagination

- **tool_service.py** (80 lines)
  - Tool registry pattern
  - Tool registration API
  - Tool execution with error handling
  - Batch tool call execution
  - Result formatting for LLM

- **rag_service.py** (140 lines)
  - ChromaDB integration
  - Document addition and removal
  - Document chunking via markitdown
  - Document querying and retrieval
  - Context generation for prompts

### Tools (Implementations)

- **web_search.py** (55 lines)
  - Google Custom Search integration
  - Query handling and result formatting
  - Graceful degradation (missing API keys)
  - Tool descriptor definition

- **web_scraper.py** (70 lines)
  - URL content extraction
  - Fallback to plain text extraction
  - Content limiting (5000 chars)
  - markitdown integration
  - Tool descriptor definition

- **rag_lookup.py** (90 lines)
  - Document search (`lookup_in_documentation`)
  - Document listing (`list_documents`)
  - Result formatting
  - Global RAG service instance
  - Tool descriptor definitions

### Utilities

- **config.py** (45 lines)
  - Centralized configuration
  - Path definitions
  - API credentials
  - Default settings
  - System instruction

- **auth.py** (65 lines)
  - Authentication wrapper
  - User registration
  - Default auth file creation
  - Wraps `components/auth/fn_auth.py`

### Package Init Files
- `__init__.py` files (one per package)
  - Module documentation strings
  - Package initialization

## Dependencies Graph

```
launch_ui.py (Main)
    ├── LLMService
    │   ├── OpenRouterClient (from components/)
    │   └── config.py
    ├── ChatInterface
    │   ├── LLMService
    │   ├── SYSTEM_INSTRUCTION (from config)
    │   └── NiceGui UI
    ├── HistoryService
    │   └── config.py (paths)
    ├── ToolService
    │   ├── web_search module
    │   ├── web_scraper module
    │   ├── rag_lookup module
    │   └── util tools
    ├── SettingsModal
    │   ├── NiceGui UI
    │   └── get_models (from components/)
    ├── DocumentPanel
    │   ├── NiceGui UI
    │   └── RAGService
    └── Authentication
        ├── utils/auth.py
        └── components/auth/fn_auth.py

RAGService
    ├── ChromaDocumentStore (from components/)
    ├── document_to_markdown (from components/)
    ├── chunk_markdown (from components/)
    └── config.py (paths)
```

## Data Flow

### Chat Request Flow
```
User Input (ChatInterface)
    ↓
LLMService.stream_completion()
    ↓
OpenRouter API (streaming chunks)
    ↓
Tool Call Detection
    ↓
ToolService.execute_tool_calls() [if tools needed]
    ↓
Tool Results
    ↓
LLMService.stream_completion() [recursive for tool results]
    ↓
Display Response (ChatInterface)
    ↓
HistoryService.save_conversation() [on completion]
```

### Document Upload Flow
```
File Upload (DocumentPanel)
    ↓
document_to_markdown() [markitdown]
    ↓
chunk_markdown() [semantic chunks]
    ↓
RAGService.add_document()
    ↓
ChromaDB.add_document() [indexing]
    ↓
Update ToolService [register rag_lookup]
    ↓
Update LLMService tools
```

### Model Selection Flow
```
SettingsModal.on_model_selected()
    ↓
get_models() [OpenRouter API]
    ↓
Model Details Display
    ↓
Save Selection
    ↓
LLMService.set_model()
    ↓
New OpenRouterClient [with new model]
```

## Configuration Paths

```
App Root: applications/advanced_chat/

Data Directory: applications/advanced_chat/data/
├── conversations/
│   └── {username}/
│       └── *.json (one per conversation)
└── rag_db/
    └── ChromaDB persistent store

Auth File: applications/advanced_chat/.passwd
Environment: applications/advanced_chat/.env
```

## Runtime Creation

These files/directories are created automatically on first run:

1. **data/** - Data directory with subdirectories
2. **data/conversations/{username}/** - Per-user conversation storage
3. **data/rag_db/** - ChromaDB vector store
4. **.passwd** - User credentials (if doesn't exist)

## Code Statistics

| Metric | Count |
|--------|-------|
| Python Files | 16 |
| Total Lines of Code | ~1,800 |
| Core Services | 4 |
| UI Components | 3 |
| Tools | 3 |
| Documentation Files | 4 |

## Import Organization

### Standard Library
- `json` - Conversation serialization
- `os`, `sys`, `pathlib` - File operations
- `uuid` - Conversation IDs
- `datetime` - Timestamps

### Third-Party
- `nicegui` - UI framework
- `openai` - LLM API client
- `requests` - HTTP calls
- `chromadb` - Vector store
- `markitdown` - Document conversion
- `bcrypt` - Password hashing
- `pandas` - Model filtering
- `dotenv` - Environment variables

### Project Components
- `components/open_router/` - LLM client
- `components/auth/` - Authentication
- `components/text_utils/` - Document processing
- `components/vectorstore/` - RAG storage

## Module Responsibilities

| Module | Phase | Responsibility |
|--------|-------|-----------------|
| chat_interface.py | 1 | Display messages, stream responses |
| llm_service.py | 1 | LLM client management |
| history_service.py | 2 | Persistence, conversation storage |
| auth.py, config.py | 2 | Authentication, configuration |
| settings_modal.py | 3 | Model selection UI |
| tool_service.py | 4 | Tool registration, execution |
| web_search.py | 4 | Google search implementation |
| web_scraper.py | 4 | Web content extraction |
| rag_lookup.py | 5 | Document search tools |
| rag_service.py | 5 | Document indexing |
| document_panel.py | 5 | Document upload UI |

## Extensibility Points

### Adding Tools
1. Create new file in `tools/`
2. Define tool function and descriptor
3. Register in `launch_ui.py` `update_tools()`

### Adding Components
1. Create new file in `components/`
2. Extend from NiceGui/existing components
3. Add to `build_authenticated_ui()`

### Adding Services
1. Create new file in `services/`
2. Define service class with public API
3. Initialize in `launch_ui.py` or other services

### Customizing UI
1. Modify `build_authenticated_ui()` in `launch_ui.py`
2. Use NiceGui components and layouts
3. Connect to services via callbacks

## Next Steps

- See **README.md** for comprehensive usage
- See **QUICKSTART.md** for 5-minute setup
- See **IMPLEMENTATION_SUMMARY.md** for technical details
- Review **launch_ui.py** (entry point) to understand integration
