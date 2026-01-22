# Quick Start Guide - Advanced LLM Chat

Get the application running in 5 minutes.

## 1. Install Dependencies (1 min)

```bash
cd applications/advanced_chat
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure API Keys (2 min)

```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your OpenRouter API key
# Get it from: https://openrouter.ai/keys
nano .env
```

Minimum required:
```
OPENROUTER_API_KEY=sk-your-api-key-here
DEFAULT_MODEL=anthropic/claude-haiku-4.5
```

Optional (for web search):
```
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

## 3. Set Up Default User (30 sec)

```bash
# Create default user (username: test, password: test)
python3 -c "from utils.auth import register_user; register_user('test', 'test')"
```

## 4. Run the Application (< 1 min)

```bash
python3 launch_ui.py
```

You should see:
```
Uvicorn running on http://127.0.0.1:7860
```

Open your browser to: **http://127.0.0.1:7860**

## 5. Login

- Username: `test`
- Password: `test`

## Take a Tour

### Chat (Left Side)
1. Type a message: "Hello! What's the capital of France?"
2. Press Enter or click Send
3. Watch the response stream in real-time

### Settings (⚙️ icon)
1. Click the settings icon in the top right
2. Go to "Model Selection" tab
3. Click "Load Available Models"
4. Select a different model (e.g., Claude 3.5 Sonnet)
5. Try a new chat with the different model

### Documents (Right Side)
1. Click on the Documents section
2. Drag and drop a PDF, Word doc, or PowerPoint file
3. Wait for it to be indexed
4. Ask a question about the document contents
5. The LLM automatically uses relevant excerpts

### Tools
The LLM can automatically use:
- **Web Search**: "Search for recent Python 3.13 features"
- **Web Scraping**: "Get the content from https://example.com"
- **Document Lookup**: Upload a doc and ask questions about it

## Common Tasks

### Create a New Conversation
Click **"New Chat"** button to clear and start fresh.

### Load a Previous Conversation
Click **"Load Recent"** button to see saved chats.

### Change the LLM Temperature
1. Settings icon → Advanced Settings tab
2. Adjust the slider
3. Click Save

### Upload Multiple Documents
1. Click upload area
2. Select multiple files at once
3. They'll be indexed automatically

## Stopping the App

Press `Ctrl+C` in your terminal

## Troubleshooting

### "API key not found"
- Make sure `.env` file exists
- Check that `OPENROUTER_API_KEY` is set
- Verify the key is valid at https://openrouter.ai/keys

### "Invalid credentials"
- For first login, use: test / test
- Or create new user:
  ```bash
  python3 -c "from utils.auth import register_user; register_user('newuser', 'password')"
  ```

### Models won't load
- Check internet connection
- Verify API key is valid
- Try clicking "Load Available Models" again
- Check console for error messages

### Document upload fails
- Ensure file is supported (PDF, DOCX, PPTX, XLSX, XLS)
- Check file size (very large files may timeout)
- Check write permissions in `applications/advanced_chat/data/`

### Memory/Performance Issues
- Clear old conversations from `data/conversations/`
- Consider reducing RAG result count
- Use smaller documents for indexing

## Next Steps

1. **Read the full README** for detailed documentation
2. **Explore the settings** to customize your experience
3. **Try different models** to find your favorite
4. **Upload your own documents** for smart Q&A
5. **Check IMPLEMENTATION_SUMMARY.md** for technical details

## Getting Help

- Check `README.md` for comprehensive documentation
- Review `IMPLEMENTATION_SUMMARY.md` for architecture
- Look at `utils/config.py` for configuration options
- Check console output for error messages

## What's Next?

### Advanced Features
- Multiple simultaneous documents
- Conversation history search
- Custom system prompts
- Model-specific optimization

### Development
- Extend with custom tools
- Add MCP server integration
- Customize UI styling
- Add voice capabilities

## Resources

- **NiceGui**: https://nicegui.io/
- **OpenRouter**: https://openrouter.ai/
- **ChromaDB**: https://docs.trychroma.com/
- **markitdown**: https://github.com/microsoft/markitdown

Enjoy chatting! 🚀
