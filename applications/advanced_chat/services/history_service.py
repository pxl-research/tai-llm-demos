"""
History Service: Manages conversation persistence and loading.
"""
import msgpack
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from typing import Optional, List

from utils.config import get_user_conversations_dir


class HistoryService:
    """Manages conversation history persistence."""

    def __init__(self, username: str = 'default'):
        """Initialize history service for a user."""
        self.username = username
        self.user_dir = get_user_conversations_dir(username)
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

        file_path = self.user_dir / f"{conversation_id}.msgpack"
        with open(file_path, 'wb') as f:
            msgpack.pack(conversation_data, f)

        return conversation_id

    def load_conversation(self, conversation_id: str) -> Optional[dict]:
        """
        Load conversation from file.

        Args:
            conversation_id: ID of conversation to load

        Returns:
            Conversation data or None if not found
        """
        file_path = self.user_dir / f"{conversation_id}.msgpack"
        if not file_path.exists():
            return None

        with open(file_path, 'rb') as f:
            return msgpack.unpack(f, raw=False)

    def list_conversations(self, limit: Optional[int] = None) -> List[dict]:
        """
        List saved conversations for the user.

        Args:
            limit: Maximum number to return (None = all)

        Returns:
            List of conversation summaries, newest first
        """
        conversations = []

        msgpack_files = sorted(
            self.user_dir.glob('*.msgpack'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Apply limit if specified
        files_to_process = msgpack_files[:limit] if limit else msgpack_files

        for file_path in files_to_process:
            with open(file_path, 'rb') as f:
                data = msgpack.unpack(f, raw=False)
                summary = {
                    'conversation_id': data['conversation_id'],
                    'created_at': data['created_at'],
                    'model': data.get('model', 'unknown'),
                    'message_count': len(data['messages']),
                    'preview': data['messages'][-1]['content'][:100] if data['messages'] else 'Empty'
                }
                conversations.append(summary)

        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation file.

        Args:
            conversation_id: ID of conversation to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        file_path = self.user_dir / f"{conversation_id}.msgpack"

        if file_path.exists():
            file_path.unlink()
            return True
        return False
