"""
Chat Interface Component: Handles message display and LLM responses.
"""
import asyncio
import html
import json
from queue import Queue
from threading import Thread
from typing import Callable, Optional
from nicegui import ui

from services.llm_service import LLMService
from utils.config import SYSTEM_INSTRUCTION


class ChatInterface:
    """Manages chat UI and message handling."""

    def __init__(self, llm_service: LLMService, tool_service=None, auto_save_callback: Callable = None):
        """Initialize chat interface with LLM service."""
        self.llm_service = llm_service
        self.tool_service = tool_service
        self.auto_save_callback = auto_save_callback
        self.conversation_id = None  # Set when first message is sent
        self.messages = [SYSTEM_INSTRUCTION.copy()]  # Initialize with system instruction
        self.chat_display = None
        self.scroll_area = None  # For auto-scrolling to bottom
        self.input_field = None
        self.send_button = None

    def build_ui(self) -> tuple:
        """
        Build the chat interface UI.

        Returns:
            Tuple of (chat_display, input_container)
        """
        # Chat display area - full width with proper scrolling
        self.scroll_area = ui.scroll_area().classes('w-full border rounded-lg shadow-inner bg-gray-50').style('height: calc(100vh - 300px)')
        self.scroll_area.props('role="log" aria-live="polite" aria-label="Chat conversation"')
        with self.scroll_area:
            self.chat_display = ui.column().classes('w-full gap-2 p-4')

        # Input area - full width
        with ui.row().classes('w-full gap-2 p-3 bg-white shadow-md rounded-lg mt-2'):
            self.input_field = ui.textarea(
                placeholder='Enter your message (Shift+Enter for newline)...',
            ).props('outlined dense autogrow aria-label="Type your message. Press Enter to send, Shift+Enter for new line"').classes('flex-grow').style('min-height: 2.5em; max-height: 15em')
            self.input_field.on('keydown.enter', lambda e: None if e.args.get('shiftKey') else self._on_send_clicked())

            self.send_button = ui.button(
                icon='send',
                on_click=self._on_send_clicked
            ).props('flat round aria-label="Send message"').classes('text-indigo-600')

        return self.chat_display, self.input_field

    async def _on_send_clicked(self, e=None):
        """Handle send button click."""
        user_input = self.input_field.value.strip()
        if not user_input:
            return

        user_message = {'role': 'user', 'content': user_input}
        self.messages.append(user_message)

        with self.chat_display:
            with ui.row().classes('w-full justify-end mb-2'):
                with ui.card().classes('bg-indigo-100 border-indigo-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                    ui.label(html.escape(user_input)).classes('whitespace-pre-wrap text-sm text-gray-800')

        self._scroll_to_bottom()

        self.input_field.value = ''

        # Get LLM response asynchronously
        await self._get_llm_response()

    async def _stream_llm_response(self, card_color: str = 'bg-white'):
        """
        Stream LLM response and handle chunk processing.

        Args:
            card_color: CSS class for message card background color

        Returns:
            Tuple of (partial_message, tool_calls)
        """
        chunk_queue = Queue()

        def stream_worker():
            """Worker thread to consume stream without blocking UI."""
            try:
                response_stream = self.llm_service.stream_completion(self.messages)
                for chunk in response_stream:
                    chunk_queue.put(chunk)
                chunk_queue.put(None)  # Sentinel value
                response_stream.close()
            except Exception as e:
                chunk_queue.put(('error', e))

        # Start worker thread
        thread = Thread(target=stream_worker, daemon=True)
        thread.start()

        partial_message = ''
        tool_calls = []
        message_markdown = None
        card_created = False
        copy_button_container = None

        # Process chunks from queue asynchronously
        while True:
            # Check for chunks without blocking
            if not chunk_queue.empty():
                chunk = chunk_queue.get()

                # Handle errors from worker thread
                if isinstance(chunk, tuple) and chunk[0] == 'error':
                    raise chunk[1]

                if chunk is None:  # Sentinel - stream complete
                    break

                if len(chunk.choices) > 0:
                    # Handle text responses
                    if chunk.choices[0].delta.content is not None:
                        if not card_created:
                            with self.chat_display:
                                with ui.row().classes('w-full mb-2'):
                                    with ui.card().classes(f'{card_color} border-gray-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                                        with ui.row().classes('w-full justify-between items-start gap-2'):
                                            with ui.column().classes('flex-grow'):
                                                message_markdown = ui.markdown('').classes('text-sm text-gray-700')
                                            # Copy button will be added after message is complete
                                            copy_button_container = ui.column()
                            card_created = True

                        partial_message += chunk.choices[0].delta.content
                        message_markdown.content = partial_message
                        self._scroll_to_bottom()

                    # Handle tool calls
                    if chunk.choices[0].delta.tool_calls is not None:
                        for tool_call_chunk in chunk.choices[0].delta.tool_calls:
                            if tool_call_chunk.index >= len(tool_calls):
                                tool_calls.insert(tool_call_chunk.index, tool_call_chunk)
                            else:
                                if tool_call_chunk.function is not None:
                                    if tool_calls[tool_call_chunk.index].function is None:
                                        tool_calls[tool_call_chunk.index].function = tool_call_chunk.function
                                    else:
                                        tool_calls[tool_call_chunk.index].function.arguments += tool_call_chunk.function.arguments

            # Yield to event loop to keep UI responsive
            await asyncio.sleep(0.01)

        # Add copy button after message is complete
        if card_created and partial_message and copy_button_container is not None:
            with copy_button_container:
                ui.button(
                    icon='content_copy',
                    on_click=lambda msg=partial_message: self._copy_to_clipboard(msg)
                ).props('flat dense round size=sm aria-label="Copy message to clipboard"').classes('text-gray-400 hover:text-gray-600')

        return partial_message, tool_calls

    async def _get_llm_response(self):
        """Stream response from LLM asynchronously."""
        try:
            partial_message, tool_calls = await self._stream_llm_response(card_color='bg-white')

            # If there's a text response, add it to history
            if partial_message:
                assistant_message = {'role': 'assistant', 'content': partial_message}
                self.messages.append(assistant_message)

            # Handle tool calls if present
            if tool_calls:
                self._handle_tool_calls(tool_calls)
                # After handling tools, continue conversation to get LLM's final response
                await self._continue_conversation_after_tools()
            else:
                if self.auto_save_callback and len(self.messages) > 1:
                    self.auto_save_callback()
        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            with self.chat_display:
                with ui.card().classes('bg-red-50 border-red-200 shadow-sm rounded-lg p-4'):
                    ui.label(error_msg).classes('text-sm text-red-700')

    async def _continue_conversation_after_tools(self, recursion_depth=0):
        """Continue conversation after tool calls to get LLM's final response."""
        MAX_RECURSION = 15  # Prevent infinite tool call loops

        if recursion_depth >= MAX_RECURSION:
            with self.chat_display:
                with ui.card().classes('bg-yellow-50 border-yellow-200 shadow-sm rounded-lg p-3'):
                    ui.label(f"⚠️ Maximum tool call depth ({MAX_RECURSION}) reached").classes('text-xs text-yellow-700')
            return

        try:
            partial_message, tool_calls = await self._stream_llm_response(card_color='bg-purple-50')

            # Add the text response to history
            if partial_message:
                assistant_message = {'role': 'assistant', 'content': partial_message}
                self.messages.append(assistant_message)

            # Handle recursive tool calls
            if tool_calls:
                self._handle_tool_calls(tool_calls)
                # Recursively continue for more tool calls
                await self._continue_conversation_after_tools(recursion_depth + 1)
            else:
                # Only auto-save when no more tool calls
                if self.auto_save_callback and len(self.messages) > 1:
                    self.auto_save_callback()

        except Exception as e:
            error_msg = f"⚠️ Error after tools: {str(e)}"
            with self.chat_display:
                with ui.card().classes('bg-red-50 border-red-200 shadow-sm rounded-lg p-4'):
                    ui.label(error_msg).classes('text-sm text-red-700')

    def _handle_tool_calls(self, tool_calls):
        """Handle tool calls from LLM response."""
        if not self.tool_service:
            return

        # Display tool execution UI
        tool_call_msg = f"🔧 Executing {len(tool_calls)} tool(s)..."
        with self.chat_display:
            with ui.card().classes('bg-amber-50 border-amber-200 shadow-sm rounded-lg p-3'):
                ui.label(tool_call_msg).classes('text-xs text-amber-700')

        # Process each tool call following the demo pattern
        for call in tool_calls:
            # Add tool call object to messages (required for LLM context)
            tool_call_obj = {
                'role': 'assistant',
                'content': None,
                'tool_calls': [
                    {
                        'id': call.id,
                        'type': 'function',
                        'function': {
                            'name': call.function.name,
                            'arguments': call.function.arguments
                        }
                    }
                ]
            }
            self.messages.append(tool_call_obj)

            # Execute the tool
            try:
                if call.function.arguments:
                    fn_args = json.loads(call.function.arguments)
                else:
                    fn_args = {}

                result = self.tool_service.execute_tool(call.function.name, fn_args)

                # Add tool response to messages
                tool_resp = {
                    'role': 'tool',
                    'name': call.function.name,
                    'tool_call_id': call.id,
                    'content': json.dumps(result)
                }
                self.messages.append(tool_resp)

                # Display tool result (collapsible with improved preview)
                with self.chat_display:
                    with ui.card().classes('bg-green-50 border-green-200 shadow-sm rounded-lg p-2'):
                        with ui.expansion(
                            self._create_tool_preview(call.function.name, result),
                            value=False  # User preference: collapsed by default
                        ).classes('text-xs border-l-4 border-green-500'):
                            formatted_result = self._format_tool_result(call.function.name, result)
                            ui.markdown(formatted_result).classes('text-sm')

                            # Raw JSON in nested expansion
                            with ui.expansion("Show raw JSON", value=False).classes('mt-2'):
                                ui.markdown(f"```json\n{json.dumps(result, indent=2)}\n```").classes('text-xs')

                self._scroll_to_bottom()

            except Exception as e:
                error_result = {'error': str(e)}
                tool_resp = {
                    'role': 'tool',
                    'name': call.function.name,
                    'tool_call_id': call.id,
                    'content': json.dumps(error_result)
                }
                self.messages.append(tool_resp)

                # Display error (collapsible with friendly message)
                friendly_error = self._humanize_error(call.function.name, e)
                with self.chat_display:
                    with ui.card().classes('bg-red-50 border-red-200 shadow-sm rounded-lg p-2'):
                        with ui.expansion(
                            f"✗ {call.function.name}: {friendly_error[:50]}...",
                            value=False
                        ).classes('text-xs border-l-4 border-red-500'):
                            ui.label(friendly_error).classes('text-sm text-red-700 mb-2')

                            # Technical details in nested expansion
                            with ui.expansion("Show technical details", value=False).classes('mt-2'):
                                ui.markdown(f"```\n{html.escape(str(e))}\n```").classes('text-xs')

                self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll the chat display to the bottom."""
        if self.scroll_area:
            self.scroll_area.scroll_to(percent=1)

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard using JavaScript."""
        ui.run_javascript(f'''
            navigator.clipboard.writeText({json.dumps(text)}).then(() => {{
                console.log('Copied to clipboard');
            }});
        ''')
        ui.notify('Copied to clipboard', type='positive', position='top')

    def _create_tool_preview(self, tool_name: str, result: dict) -> str:
        """
        Create a brief preview for collapsed tool result.

        Returns:
            Short preview text (under 60 chars)
        """
        if tool_name == 'search_on_google':
            count = len(result.get('items', []))
            return f"✓ {tool_name}: Found {count} results"

        elif tool_name == 'get_webpage_content':
            return f"✓ {tool_name}: Page fetched successfully"

        elif tool_name == 'lookup_in_documentation':
            count = len(result.get('results', []))
            return f"✓ {tool_name}: Found {count} documents"

        elif tool_name == 'list_documents':
            count = len(result.get('documents', []))
            return f"✓ {tool_name}: {count} documents indexed"

        else:
            return f"✓ {tool_name}: Completed"

    def _format_tool_result(self, tool_name: str, result: dict) -> str:
        """
        Format tool result as user-friendly text.
        """
        # Google search
        if tool_name == 'search_on_google':
            if 'error' in result:
                return f"**Error:** {result['error']}"
            items = result.get('items', [])
            if not items:
                return "No results found."

            formatted = "### Search Results\n\n"
            for i, item in enumerate(items[:5], 1):
                formatted += f"**{i}. [{item['title']}]({item['link']})**\n"
                formatted += f"   {item.get('snippet', '')}\n\n"
            return formatted

        # Web scraper
        elif tool_name == 'get_webpage_content':
            if 'error' in result:
                return f"**Error:** {result['error']}"
            content = result.get('content', '')
            return f"**Page Content** (first 500 characters):\n\n{content[:500]}..."

        # RAG lookup
        elif tool_name == 'lookup_in_documentation':
            if 'error' in result:
                return f"**Error:** {result['error']}"
            results = result.get('results', [])
            if not results:
                return "No relevant documents found."

            formatted = "### Found in Documents\n\n"
            for doc in results:
                source = doc.get('source', 'Unknown')
                content_preview = doc.get('content', '')[:200]
                formatted += f"**{source}:** {content_preview}...\n\n"
            return formatted

        # List documents
        elif tool_name == 'list_documents':
            docs = result.get('documents', [])
            if not docs:
                return "No documents uploaded yet."
            return "**Indexed Documents:**\n\n" + "\n".join(f"- {doc}" for doc in docs)

        # Default: Show formatted JSON
        else:
            return f"```json\n{json.dumps(result, indent=2)}\n```"

    def _humanize_error(self, tool_name: str, exception: Exception) -> str:
        """
        Convert exception to user-friendly message.
        """
        error_str = str(exception).lower()

        # Network errors
        if 'connection' in error_str or 'timeout' in error_str:
            return f"Cannot connect to {tool_name}. Check your internet connection."

        # API key errors
        if 'api key' in error_str or 'unauthorized' in error_str or '401' in error_str:
            return f"{tool_name} requires a valid API key. Check your .env configuration."

        # Rate limiting
        if 'rate limit' in error_str or '429' in error_str:
            return f"{tool_name} is rate-limited. Please wait a moment and try again."

        # Permission errors
        if 'permission' in error_str or 'forbidden' in error_str or '403' in error_str:
            return f"Permission denied when accessing {tool_name}."

        # Not found
        if 'not found' in error_str or '404' in error_str:
            return f"Resource not found in {tool_name}."

        # Generic error with first 100 chars
        return f"{tool_name} failed: {str(exception)[:100]}"

    def push_message(self, content: str, role: str = 'assistant'):
        """Push a message to the chat display."""
        with self.chat_display:
            if role == 'user':
                with ui.row().classes('w-full justify-end mb-2'):
                    with ui.card().classes('bg-indigo-100 border-indigo-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                        ui.label(html.escape(content)).classes('whitespace-pre-wrap text-sm text-gray-800')
            else:
                with ui.row().classes('w-full mb-2'):
                    with ui.card().classes('bg-white border-gray-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                        with ui.row().classes('w-full justify-between items-start gap-2'):
                            with ui.column().classes('flex-grow'):
                                ui.markdown(content).classes('text-sm text-gray-700')
                            ui.button(
                                icon='content_copy',
                                on_click=lambda: self._copy_to_clipboard(content)
                            ).props('flat dense round size=sm').classes('text-gray-400 hover:text-gray-600')

    def get_messages(self) -> list:
        """Get current message history."""
        return self.messages.copy()

    def clear_chat(self):
        """Clear chat history."""
        self.messages = [SYSTEM_INSTRUCTION.copy()]
        self.chat_display.clear()
        self.input_field.value = ''
