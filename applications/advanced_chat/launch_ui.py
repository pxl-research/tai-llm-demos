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
from services.settings_service import SettingsService
from components.chat_interface import ChatInterface
from components.settings_modal import SettingsModal
from components.document_panel import DocumentPanel
from utils.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE
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
settings_service = None
settings_modal = None
document_panel = None
model_label = None


def update_tools():
    """Update available tools based on documents and settings."""
    if not tool_service:
        return

    # Clear existing tools to avoid duplicates
    tool_service.clear_tools()

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
        if settings_service:
            settings_service.update_setting('model', model_name)
        if model_label:
            model_label.text = f"Currently using: {model_name}"


def on_settings_changed(settings: dict):
    """Handle settings change."""
    if 'temperature' in settings and llm_service:
        llm_service.set_temperature(settings['temperature'])
        if settings_service:
            settings_service.update_setting('temperature', settings['temperature'])


def on_document_added(doc_name: str):
    """Handle document addition."""
    update_tools()
    ui.notify(f'Document "{doc_name}" added to RAG')


def on_document_removed(doc_name: str):
    """Handle document removal."""
    update_tools()
    ui.notify(f'Document "{doc_name}" removed from RAG')


def auto_save_conversation():
    """Auto-save conversation after each message."""
    if not history_service or not chat_interface:
        return

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
        ui.notify(f"Auto-save error: {str(e)[:50]}", type='warning')


def build_authenticated_ui():
    """Build the main authenticated application UI."""
    global llm_service, chat_interface, history_service, tool_service, rag_service, document_panel, settings_modal, settings_service, model_label

    # Initialize settings service and load user preferences
    settings_service = SettingsService(current_user)
    user_settings = settings_service.load_settings()

    # Initialize services with current user and saved settings
    llm_service = LLMService(
        model_name=user_settings.get('model', DEFAULT_MODEL),
        temperature=user_settings.get('temperature', DEFAULT_TEMPERATURE)
    )
    history_service = HistoryService(current_user)
    tool_service = ToolService(None)
    rag_service = RAGService(current_user)

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
                ui.button(
                    f'User: {current_user}',
                    icon='person',
                    on_click=lambda: show_logout_dialog()
                ).props('flat aria-label="User menu - click to logout"').classes('text-sm hover:bg-white/10')
                ui.button(
                    icon='settings',
                    on_click=lambda: settings_modal.show()
                ).props('flat round aria-label="Open settings"')

    # Model indicator
    model_label = ui.label().classes('text-center text-xs text-gray-500 py-2 bg-gray-50')
    model_label.text = f"Currently using: {llm_service.model_name}"

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
            ).props('outline aria-label="Start new conversation"').classes('rounded-md')

            ui.button(
                'Load Recent',
                on_click=lambda: show_recent_conversations(),
                icon='history'
            ).props('outline aria-label="Load conversation history"').classes('rounded-md')

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
        .props('fab aria-label="Open documents panel"') \
        .classes('fixed bottom-6 right-6') \
        .style('background: linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234))')

    # Initialize tools
    update_tools()


def show_recent_conversations():
    """Show dialog with all conversations in scrollable list."""
    # Load ALL conversations (no limit)
    conversations = history_service.list_conversations(limit=None)

    def delete_conversation_ui(conversation_id: str, dialog):
        """Delete with confirmation."""
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label('Delete Conversation?').classes('text-lg font-semibold')
            ui.label('This action cannot be undone.').classes('text-sm text-gray-600 mt-2')

            with ui.row().classes('gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button('Delete', on_click=lambda: (
                    history_service.delete_conversation(conversation_id),
                    confirm_dialog.close(),
                    dialog.close(),
                    show_recent_conversations(),
                    ui.notify('Conversation deleted', type='positive')
                )).props('color=negative')

        confirm_dialog.open()

    with ui.dialog() as dialog:
        with ui.card().classes('w-full').style('min-width: 50%; max-width: 70%; max-height: 80vh'):
            # Header
            with ui.row().classes('w-full items-center justify-between mb-3'):
                ui.label('Conversation History').classes('text-h6 font-bold')
                ui.label(f'{len(conversations)} total').classes('text-sm text-gray-500')

            # Search input
            search_input = ui.input(
                placeholder='Search conversations...'
            ).classes('w-full mb-3').props('outlined dense clearable')

            # Scrollable list (simple chronological order - user preference)
            results_scroll = ui.scroll_area().classes('w-full').style('height: 55vh')

            with results_scroll:
                results_container = ui.column().classes('w-full gap-2')

            def render_conversations(search_term: str = ''):
                """Render conversations with optional search filter."""
                results_container.clear()

                with results_container:
                    if not conversations:
                        ui.label('No conversations yet').classes('text-gray-500 text-center py-8')
                        return

                    # Filter by search term
                    if search_term:
                        filtered = [
                            c for c in conversations
                            if search_term.lower() in c['preview'].lower()
                            or search_term.lower() in c.get('model', '').lower()
                        ]
                    else:
                        filtered = conversations

                    if not filtered:
                        ui.label('No matching conversations').classes('text-gray-500 text-center py-8')
                        return

                    # Simple chronological list (newest first)
                    for conv in filtered:
                        with ui.card().classes('w-full bg-gray-50 border hover:bg-gray-100 transition-colors p-3'):
                            with ui.row().classes('w-full items-start gap-3'):
                                # Left: info
                                with ui.column().classes('flex-grow'):
                                    # Date and metadata
                                    from datetime import datetime
                                    conv_datetime = datetime.fromisoformat(conv['created_at'])
                                    date_str = conv_datetime.strftime('%Y-%m-%d %I:%M %p')

                                    ui.label(
                                        f"📅 {date_str} • {conv['message_count']} msgs • {conv.get('model', 'unknown')}"
                                    ).classes('text-xs text-gray-600')

                                    # Preview
                                    ui.label(conv['preview']).classes('text-sm mt-1 break-words')

                                # Right: actions
                                with ui.row().classes('gap-1 flex-shrink-0'):
                                    ui.button(
                                        icon='folder_open',
                                        on_click=lambda c=conv: load_conversation(c['conversation_id'], dialog)
                                    ).props('flat dense round aria-label="Load conversation"').classes('text-blue-600')

                                    ui.button(
                                        icon='delete',
                                        on_click=lambda c=conv: delete_conversation_ui(c['conversation_id'], dialog)
                                    ).props('flat dense round aria-label="Delete conversation"').classes('text-red-600')

            # Wire search
            search_input.on('input', lambda e: render_conversations(e.value))

            # Initial render
            render_conversations()

            # Close button
            ui.button('Close', on_click=dialog.close).props('flat').classes('mt-3')

    dialog.open()


def load_conversation(conv_id: str, dialog):
    """Load a saved conversation."""
    conv_data = history_service.load_conversation(conv_id)
    if conv_data:
        # Restore messages to chat interface
        chat_interface.messages = conv_data['messages']

        # Clear the current display
        chat_interface.chat_display.clear()

        # Re-display each message (skip system instruction at index 0)
        for msg in conv_data['messages'][1:]:
            chat_interface.push_message(msg['content'], role=msg['role'])

        # Scroll to bottom to show latest messages
        chat_interface._scroll_to_bottom()

        dialog.close()
        ui.notify('Conversation loaded', type='positive')


def on_login(username: str, password: str):
    """Handle login."""
    global current_user

    if not authenticate(username, password):
        return False

    current_user = username
    return True


def perform_logout():
    """Perform logout by clearing session and reloading page."""
    global current_user
    current_user = None
    ui.run_javascript('window.location.reload()')


def show_logout_dialog():
    """Show logout confirmation dialog."""
    with ui.dialog() as logout_dialog, ui.card().style('padding: 24px; border-radius: 2px; max-width: 400px'):
        ui.label('Logout Confirmation').style('font-size: 18px; font-weight: 600; color: #1a1a1a; margin-bottom: 12px')
        ui.label(f'Are you sure you want to logout, {current_user}?').style('font-size: 14px; color: #737373; margin-bottom: 20px')

        with ui.row().classes('gap-2 w-full').style('justify-content: flex-end'):
            ui.button('Cancel', on_click=lambda: logout_dialog.close()).props('flat').style('color: #525252')
            ui.button('Logout', on_click=lambda: perform_logout()).style('background: #262626; color: white; border-radius: 2px')

    logout_dialog.open()


def build_login_ui():
    """Build a clean, elegant login interface."""

    # Simplified CSS - uses NiceGui's native styling with minimal overrides
    ui.add_head_html('''
        <style>
            body {
                background-color: #fafafa;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .login-container {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 1rem;
            }

            .login-card {
                background: white;
                border-radius: 2px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.08);
                padding: 2.5rem;
                width: 100%;
                max-width: 380px;
            }

            .login-title {
                font-size: 21px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.5rem;
                text-align: center;
            }

            .login-subtitle {
                font-size: 14px;
                color: #737373;
                margin-bottom: 2rem;
                text-align: center;
            }

            .login-button {
                width: 100%;
                height: 44px;
                background: #262626;
                color: white;
                border-radius: 2px;
                transition: background-color 0.2s;
            }

            .login-button:hover {
                background: #171717;
            }

            .error-message {
                color: #dc2626;
                font-size: 14px;
                margin-top: 0.5rem;
            }

            .login-button.loading {
                position: relative;
                color: transparent;
            }

            .login-button.loading::after {
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                top: 50%;
                left: 50%;
                margin-left: -8px;
                margin-top: -8px;
                border: 2px solid #ffffff;
                border-bottom-color: transparent;
                border-radius: 50%;
                animation: spin 600ms linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Keyboard focus indicators */
            button:focus-visible,
            input:focus-visible,
            textarea:focus-visible {
                outline: 2px solid rgb(79, 70, 229) !important;
                outline-offset: 2px;
            }

            .q-card:focus-visible {
                outline: 2px solid rgb(79, 70, 229);
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
            }
        </style>
    ''')

    # Container
    with ui.column().classes('login-container'):
        with ui.card().classes('login-card'):
            # Header
            ui.label('Advanced Chat').classes('login-title')
            ui.label('Sign in to continue').classes('login-subtitle')

            # Username field
            username_input = ui.input('Username', placeholder='Enter username').props('outlined dense').classes('mb-3')

            # Password field
            password_input = ui.input('Password', placeholder='Enter password', password=True).props('outlined dense').classes('mb-3')

            # Error message
            error_message = ui.label('').classes('error-message').style('display: none')

            # Login button
            login_button = ui.button('Sign In').classes('login-button')

    # Login handler with validation and loading states
    async def login_clicked():
        """Handle login with proper validation and feedback."""
        # Clear previous errors
        error_message.style('display: none')
        error_message.text = ''

        # Get values
        username = username_input.value.strip() if username_input.value else ''
        password = password_input.value.strip() if password_input.value else ''

        # Validate fields
        if not username:
            error_message.text = 'Please enter your username'
            error_message.style('display: block')
            return

        if not password:
            error_message.text = 'Please enter your password'
            error_message.style('display: block')
            return

        # Show loading state
        login_button.classes(add='loading')
        username_input.disable()
        password_input.disable()

        # Attempt authentication
        try:
            if on_login(username, password):
                # Success - navigate to trigger page rebuild
                ui.run_javascript("window.location.href = '/';")
            else:
                # Failed - show error
                error_message.text = 'Invalid username or password'
                error_message.style('display: block')
                # Remove loading state
                login_button.classes(remove='loading')
                username_input.enable()
                password_input.enable()
        except Exception as e:
            # Show actual error for debugging
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            error_message.text = f'Error: {str(e)}'
            error_message.style('display: block')
            # Remove loading state
            login_button.classes(remove='loading')
            username_input.enable()
            password_input.enable()

    # Clear errors on input
    def clear_error():
        error_message.style('display: none')

    username_input.on('focus', clear_error)
    password_input.on('focus', clear_error)

    # Button click handler
    login_button.on('click', login_clicked)

    # Enter key handlers
    username_input.on('keydown.enter', login_clicked)
    password_input.on('keydown.enter', login_clicked)


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
