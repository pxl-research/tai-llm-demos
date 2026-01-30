"""
Settings Service: Manages user settings persistence.
"""
import json
from pathlib import Path
from typing import Any, Dict

from utils.config import get_user_settings_path, DEFAULT_MODEL, DEFAULT_TEMPERATURE


class SettingsService:
    """Manage user settings persistence."""

    def __init__(self, username: str):
        """
        Initialize settings service for a user.

        Args:
            username: Username for settings isolation
        """
        self.username = username
        self.settings_path = get_user_settings_path(username)
        self._ensure_settings_file()

    def _ensure_settings_file(self):
        """Create default settings file if it doesn't exist."""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.settings_path.exists():
            default_settings = {
                'model': DEFAULT_MODEL,
                'temperature': DEFAULT_TEMPERATURE,
            }
            self.save_settings(default_settings)

    def load_settings(self) -> Dict[str, Any]:
        """
        Load user settings from file.

        Returns:
            Dictionary of user settings
        """
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {
                'model': DEFAULT_MODEL,
                'temperature': DEFAULT_TEMPERATURE,
            }

    def save_settings(self, settings: Dict[str, Any]):
        """
        Save user settings to file.

        Args:
            settings: Dictionary of settings to save
        """
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

    def update_setting(self, key: str, value: Any):
        """
        Update a single setting.

        Args:
            key: Setting key to update
            value: New value for the setting
        """
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)

    def get_setting(self, key: str, default=None) -> Any:
        """
        Get a single setting value.

        Args:
            key: Setting key to retrieve
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        settings = self.load_settings()
        return settings.get(key, default)
