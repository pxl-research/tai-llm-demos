"""
Chat Interface Component: Handles message display and LLM responses.
"""
import html
import json
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
        self.input_field = None
        self.send_button = None

    def build_ui(self) -> tuple:
        """
        Build the chat interface UI.

        Returns:
            Tuple of (chat_display, input_container)
        """
        # Chat display area - full width
        with ui.column().classes('w-full flex-grow overflow-auto border rounded-lg shadow-inner p-4 bg-gray-50').style('min-height: 400px'):
            self.chat_display = ui.column().classes('w-full gap-2')

        # Input area - full width
        with ui.row().classes('w-full gap-2 p-3 bg-white shadow-md rounded-lg mt-2'):
            self.input_field = ui.input(
                placeholder='Enter your message...',
            ).props('outlined dense').classes('flex-grow')
            self.input_field.on('keydown.enter', lambda: self._on_send_clicked())

            self.send_button = ui.button(
                icon='send',
                on_click=self._on_send_clicked
            ).props('flat round').classes('text-indigo-600')

        return self.chat_display, self.input_field

    def _on_send_clicked(self, e=None):
        """Handle send button click."""
        user_input = self.input_field.value.strip()
        if not user_input:
            return

        # Add user message to history
        user_message = {'role': 'user', 'content': user_input}
        self.messages.append(user_message)

        # Display user message (right-aligned)
        with self.chat_display:
            with ui.row().classes('w-full justify-end mb-2'):
                with ui.card().classes('bg-indigo-100 border-indigo-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                    ui.label(html.escape(user_input)).classes('whitespace-pre-wrap text-sm text-gray-800')

        # Clear input
        self.input_field.value = ''

        # Get LLM response
        self._get_llm_response()

    def _get_llm_response(self):
        """Stream response from LLM."""
        try:
            response_stream = self.llm_service.stream_completion(self.messages)

            partial_message = ''
            tool_calls = []

            # Create assistant message card (left-aligned)
            with self.chat_display:
                with ui.row().classes('w-full mb-2'):
                    with ui.card().classes('bg-white border-gray-200 shadow-sm rounded-lg p-4').style('max-width: 75%'):
                        message_markdown = ui.markdown('').classes('text-sm text-gray-700')

            for chunk in response_stream:
                if len(chunk.choices) > 0:
                    # Handle text responses
                    if chunk.choices[0].delta.content is not None:
                        partial_message += chunk.choices[0].delta.content
                        message_markdown.content = partial_message

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

            response_stream.close()

            # If there's a text response, add it to history
            if partial_message:
                assistant_message = {'role': 'assistant', 'content': partial_message}
                self.messages.append(assistant_message)

            # Handle tool calls if present
            if tool_calls:
                self._handle_tool_calls(tool_calls)
                # After handling tools, continue conversation to get LLM's final response
                self._continue_conversation_after_tools()
            else:
                # No tools, just auto-save
                if self.auto_save_callback and len(self.messages) > 1:
                    self.auto_save_callback()
        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            with self.chat_display:
                with ui.card().classes('bg-red-50 border-red-200 shadow-sm rounded-lg p-4'):
                    ui.label(error_msg).classes('text-sm text-red-700')

    def _continue_conversation_after_tools(self):
        """Continue conversation after tool calls to get LLM's final response."""
        try:
            response_stream = self.llm_service.stream_completion(self.messages)

            partial_message = ''
            with self.chat_display:
                with ui.row().classes('w-full mb-2'):
                    with ui.card().classes('bg-purple-50 border-purple-200 shadow-sm rounded-lg p-4'):
                        message_markdown = ui.markdown('').classes('text-sm text-gray-700')

            for chunk in response_stream:
                if len(chunk.choices) > 0:
                    if chunk.choices[0].delta.content is not None:
                        partial_message += chunk.choices[0].delta.content
                        message_markdown.content = partial_message

            response_stream.close()

            # Add the final response
            if partial_message:
                assistant_message = {'role': 'assistant', 'content': partial_message}
                self.messages.append(assistant_message)

                # Auto-save after response completes
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

                # Display tool result
                with self.chat_display:
                    with ui.card().classes('bg-green-50 border-green-200 shadow-sm rounded-lg p-3'):
                        result_json = json.dumps(result, indent=2)
                        result_markdown = f"**✓ {call.function.name}**\n\n```json\n{result_json}\n```"
                        ui.markdown(result_markdown).classes('text-xs text-green-700')

            except Exception as e:
                error_result = {'error': str(e)}
                tool_resp = {
                    'role': 'tool',
                    'name': call.function.name,
                    'tool_call_id': call.id,
                    'content': json.dumps(error_result)
                }
                self.messages.append(tool_resp)

                # Display error
                with self.chat_display:
                    with ui.card().classes('bg-red-50 border-red-200 shadow-sm rounded-lg p-3'):
                        error_markdown = f"**✗ {call.function.name}**\n\n```\n{html.escape(str(e))}\n```"
                        ui.markdown(error_markdown).classes('text-xs text-red-700')

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
                        ui.markdown(content).classes('text-sm text-gray-700')

    def get_messages(self) -> list:
        """Get current message history."""
        return self.messages.copy()

    def clear_chat(self):
        """Clear chat history."""
        self.messages = [SYSTEM_INSTRUCTION.copy()]
        self.chat_display.clear()
        self.input_field.value = ''
