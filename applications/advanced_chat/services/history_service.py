"""
History Service: Manages conversation persistence and loading.
"""
import json
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
                summary = {
                    'conversation_id': data['conversation_id'],
                    'created_at': data['created_at'],
                    'model': data['model'],
                    'message_count': len(data['messages']),
                    'preview': data['messages'][-1]['content'][:100] if data['messages'] else 'Empty'
                }
                conversations.append(summary)

        return conversations
