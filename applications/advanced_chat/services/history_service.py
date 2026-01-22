"""
History Service: Manages conversation persistence and loading.
"""
import json
import os
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from typing import Optional, List

from utils.config import CONVERSATIONS_DIR


class HistoryService:
    """Manages conversation history persistence."""

    def __init__(self, username: str = 'default'):
        """Initialize history service for a user."""
        self.username = username
        self.user_dir = CONVERSATIONS_DIR / username
        self.user_dir.mkdir(parents=True, exist_ok=True)

    def save_conversation(
        self,
        messages: List[dict],
        conversation_id: Optional[str] = None,
        model: str = 'default',
        settings: Optional[dict] = None
    ) -> str:
        """
        Save conversation to file.

        Args:
            messages: List of message dicts
            conversation_id: Unique ID for conversation (generated if None)
            model: Model name used in conversation
            settings: Additional settings dict

        Returns:
            The conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid4())

        if settings is None:
            settings = {}

        conversation_data = {
            'conversation_id': conversation_id,
            'user': self.username,
            'created_at': datetime.now().isoformat(),
            'messages': messages,
            'model': model,
            'settings': settings
        }

        # Save to JSON file
        file_path = self.user_dir / f"{conversation_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        return conversation_id

    def load_conversation(self, conversation_id: str) -> Optional[dict]:
        """
        Load conversation from file.

        Args:
            conversation_id: ID of conversation to load

        Returns:
            Conversation data or None if not found
        """
        file_path = self.user_dir / f"{conversation_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_conversations(self, limit: int = 20) -> List[dict]:
        """
        List saved conversations for the user.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation summaries
        """
        conversations = []

        json_files = sorted(
            self.user_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for file_path in json_files[:limit]:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Create summary
                summary = {
                    'conversation_id': data['conversation_id'],
                    'created_at': data['created_at'],
                    'model': data['model'],
                    'message_count': len(data['messages']),
                    'preview': data['messages'][-1]['content'][:100] if data['messages'] else 'Empty'
                }
                conversations.append(summary)

        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: ID of conversation to delete

        Returns:
            True if deleted, False if not found
        """
        file_path = self.user_dir / f"{conversation_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_conversation_preview(self, conversation_id: str, max_messages: int = 5) -> Optional[dict]:
        """
        Get a preview of a conversation with limited messages.

        Args:
            conversation_id: ID of conversation
            max_messages: Maximum number of recent messages to return

        Returns:
            Conversation data with limited messages or None
        """
        conv_data = self.load_conversation(conversation_id)
        if not conv_data:
            return None

        # Keep only system message and last max_messages
        messages = conv_data['messages']
        if len(messages) > max_messages + 1:  # +1 for system message
            # Keep system message and last max_messages
            conv_data['messages'] = [messages[0]] + messages[-(max_messages):]

        return conv_data

    def export_conversation(self, conversation_id: str, output_format: str = 'json') -> Optional[str]:
        """
        Export conversation to a different format.

        Args:
            conversation_id: ID of conversation
            output_format: Format to export ('json', 'md', 'txt')

        Returns:
            Exported content or None if not found
        """
        conv_data = self.load_conversation(conversation_id)
        if not conv_data:
            return None

        if output_format == 'json':
            return json.dumps(conv_data, indent=2, ensure_ascii=False)

        elif output_format == 'md':
            # Markdown format
            lines = [
                f"# Conversation: {conv_data['conversation_id']}",
                f"**Model:** {conv_data['model']}",
                f"**Created:** {conv_data['created_at']}",
                f"**User:** {conv_data['user']}",
                "",
            ]
            for msg in conv_data['messages']:
                if msg['role'] == 'system':
                    continue
                lines.append(f"## {msg['role'].upper()}")
                lines.append(msg['content'])
                lines.append("")
            return '\n'.join(lines)

        elif output_format == 'txt':
            # Plain text format
            lines = [
                f"Conversation ID: {conv_data['conversation_id']}",
                f"Model: {conv_data['model']}",
                f"Created: {conv_data['created_at']}",
                f"User: {conv_data['user']}",
                "",
                "-" * 80,
                ""
            ]
            for msg in conv_data['messages']:
                if msg['role'] == 'system':
                    continue
                lines.append(f"{msg['role'].upper()}:")
                lines.append(msg['content'])
                lines.append("")
            return '\n'.join(lines)

        return None
