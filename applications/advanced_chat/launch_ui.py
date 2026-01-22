#!/usr/bin/env python3
"""
Advanced NiceGui LLM Chat Application - Complete Implementation
Phases 1-5 integrated: Core Chat UI, Persistence, Model Selection, Tools, RAG
Main entry point for the application.
"""
import json
from uuid import uuid4

from nicegui import ui
from services.llm_service import LLMService
from services.history_service import HistoryService
from services.tool_service import ToolService
from services.rag_service import RAGService
from components.chat_interface import ChatInterface
from components.settings_modal import SettingsModal
from components.document_panel import DocumentPanel
from utils.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, SYSTEM_INSTRUCTION
from utils.auth import authenticate
from tools.web_search import search_on_google, search_descriptor
from tools.web_scraper import get_webpage_content, scraper_descriptor
from tools.rag_lookup import lookup_in_documentation, list_documents, rag_lookup_descriptor, list_docs_descriptor, set_rag_service

# Global state
current_user = None
llm_service = None
chat_interface = None
history_service = None
tool_service = None
rag_service = None
settings_modal = None
document_panel = None


def update_tools():
    """Update available tools based on documents and settings."""
    if not tool_service:
        return

    # Clear existing tools to avoid duplicates
    tool_service.clear_tools()

    # Register tools
    tool_service.register_tool('search_on_google', search_on_google, search_descriptor)
    tool_service.register_tool('get_webpage_content', get_webpage_content, scraper_descriptor)
    tool_service.register_tool('lookup_in_documentation', lookup_in_documentation, rag_lookup_descriptor)
    tool_service.register_tool('list_documents', list_documents, list_docs_descriptor)

    # Update LLM with tools
    llm_service.set_tools(tool_service.get_tools_for_llm())


def on_model_changed(model_name: str):
    """Handle model change."""
    if llm_service:
        llm_service.set_model(model_name)


def on_settings_changed(settings: dict):
    """Handle settings change."""
    if 'temperature' in settings and llm_service:
        llm_service.set_temperature(settings['temperature'])


def on_document_added(doc_name: str):
    """Handle document addition."""
    update_tools()
    ui.notify(f'Document "{doc_name}" added to RAG')


def on_document_removed(doc_name: str):
    """Handle document removal."""
    update_tools()
    ui.notify(f'Document "{doc_name}" removed from RAG')


def handle_tool_execution(tool_name: str, args: dict, result: dict):
    """Handle tool execution callback."""
    print(f"Tool executed: {tool_name}")


def auto_save_conversation():
    """Auto-save conversation after each message."""
    if not history_service or not chat_interface:
        return

    # Generate conversation_id on first save
    if not chat_interface.conversation_id:
        chat_interface.conversation_id = str(uuid4())

    try:
        history_service.save_conversation(
            messages=chat_interface.messages,
            conversation_id=chat_interface.conversation_id,
            model=llm_service.model_name,
            settings={'temperature': llm_service.temperature}
        )
    except Exception as e:
        print(f"Auto-save error: {e}")


def build_authenticated_ui():
    """Build the main authenticated application UI."""
    global llm_service, chat_interface, history_service, tool_service, rag_service, document_panel

    # Initialize services with current user
    llm_service = LLMService(
        model_name=DEFAULT_MODEL,
        temperature=DEFAULT_TEMPERATURE
    )
    history_service = HistoryService(current_user)
    tool_service = ToolService(handle_tool_execution)
    rag_service = RAGService()

    # Initialize chat interface with auto-save callback
    chat_interface = ChatInterface(llm_service, tool_service=tool_service, auto_save_callback=auto_save_conversation)

    # Set shared RAG service for tools
    set_rag_service(rag_service)

    # Initialize settings modal
    settings_modal = SettingsModal(on_model_changed, on_settings_changed)
    settings_modal.build_ui()

    # Header with gradient
    with ui.header().classes('w-full text-white').style('background: linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234))').props('elevated'):
        with ui.row().classes('w-full items-center justify-between px-4'):
            ui.label('Advanced LLM Chat').classes('text-h5 font-bold')
            with ui.row().classes('gap-2'):
                ui.label(f'User: {current_user}').classes('text-sm')
                ui.button(
                    icon='settings',
                    on_click=lambda: settings_modal.show()
                ).props('flat round')

    # Main content area - full width container
    with ui.column().classes('w-full flex-grow items-center p-4').style('height: calc(100vh - 120px)'):
        # Chat takes full width of container, then centers content
        with ui.column().classes('w-full').style('max-width: 1400px'):
            chat_interface.build_ui()

        # Conversation controls - centered to match chat
        with ui.row().classes('gap-2 mt-2').style('max-width: 1200px; width: 100%'):
            def on_new_chat():
                # Generate new conversation ID for next chat
                chat_interface.conversation_id = None
                chat_interface.clear_chat()
                ui.notify('New conversation started', type='positive')

            ui.button(
                'New Chat',
                on_click=on_new_chat,
                icon='refresh'
            ).props('outline').classes('rounded-md')

            ui.button(
                'Load Recent',
                on_click=lambda: show_recent_conversations(),
                icon='history'
            ).props('outline').classes('rounded-md')

    # Drawer for documents (right side) - wider drawer
    with ui.right_drawer(fixed=False).props('bordered overlay width=600') as drawer:
        drawer.value = False  # Closed by default
        with ui.column().classes('w-full gap-3 p-4 h-full overflow-auto'):
            # Header with close button
            with ui.row().classes('w-full items-center justify-between mb-2'):
                ui.label('Documents & Tools').classes('text-lg font-semibold text-gray-800')
                ui.button(icon='close', on_click=drawer.toggle) \
                    .props('flat round') \
                    .classes('text-gray-600')

            ui.separator()

            # Documents section
            document_panel = DocumentPanel(rag_service, on_document_added, on_document_removed)
            document_panel.build_ui()

    # Floating button to toggle drawer
    ui.button(icon='description', on_click=drawer.toggle) \
        .props('fab') \
        .classes('fixed bottom-6 right-6') \
        .style('background: linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234))')

    # Initialize tools
    update_tools()


def show_recent_conversations():
    """Show dialog with recent conversations."""
    conversations = history_service.list_conversations(5)

    with ui.dialog() as dialog:
        with ui.card().classes('w-full max-w-md'):
            ui.label('Recent Conversations').classes('text-h6 font-bold')

            if not conversations:
                ui.label('No saved conversations').classes('text-gray-500')
            else:
                for conv in conversations:
                    with ui.card().classes('w-full'):
                        with ui.column().classes('w-full'):
                            ui.label(conv['created_at'][:10]).classes('text-sm text-gray-600')
                            ui.label(f"Messages: {conv['message_count']}").classes('text-xs')
                            ui.label(conv['preview']).classes('text-sm truncate')
                            ui.button(
                                'Load',
                                on_click=lambda cid=conv['conversation_id']: load_conversation(cid, dialog)
                            ).props('outline small').classes('w-full')

            ui.button('Close', on_click=dialog.close).props('flat').classes('w-full mt-4')

    dialog.open()


def load_conversation(conv_id: str, dialog):
    """Load a saved conversation."""
    conv_data = history_service.load_conversation(conv_id)
    if conv_data:
        # Restore messages (skip system message)
        chat_interface.messages = conv_data['messages']
        chat_interface.chat_display.value = [
            {'content': msg['content'], 'avatar': '👤' if msg['role'] == 'user' else '🤖'}
            for msg in conv_data['messages'][1:]  # Skip system instruction
        ]
        chat_interface.chat_display.refresh()
        dialog.close()
        ui.notify('Conversation loaded')


def on_login(username: str, password: str):
    """Handle login."""
    global current_user

    if not authenticate(username, password):
        ui.notify('Invalid credentials', type='negative')
        return False

    current_user = username
    return True


def build_login_ui():
    """Build the login UI."""
    with ui.card().classes('absolute-center'):
        ui.label('Advanced LLM Chat').classes('text-h4 font-bold text-center')

        username_input = ui.input(label='Username', placeholder='Enter username')
        password_input = ui.input(
            label='Password',
            placeholder='Enter password',
            password=True
        )

        def login_clicked():
            username = username_input.value.strip()
            password = password_input.value.strip()

            if not username or not password:
                ui.notify('Please fill all fields', type='warning')
                return

            if on_login(username, password):
                # Clear login UI and show main app
                ui.run_javascript('window.location.reload()')

        ui.button('Login', on_click=login_clicked).classes('w-full')
        ui.label('Demo: username=test, password=test').classes('text-xs text-gray-600 text-center')


@ui.page('/')
def main_page():
    """Main application page."""
    if current_user is None:
        build_login_ui()
    else:
        build_authenticated_ui()


# Run the app
if __name__ == '__main__':
    ui.run(
        host='127.0.0.1',
        port=7860,
        title='Advanced LLM Chat',
        reload=False
    )
