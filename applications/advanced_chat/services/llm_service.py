"""
LLM Service: Manages interactions with OpenRouter LLM client.
"""
from typing import Iterable, Optional

from utils.open_router_client import OpenRouterClient
from utils.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, SYSTEM_INSTRUCTION


class LLMService:
    """Manages LLM client and interactions."""

    def __init__(self, model_name: str, tools_list: Optional[Iterable] = None, temperature: float = 0.7):
        """Initialize LLM service with specified model."""
        self.model_name = model_name
        self.temperature = temperature
        self.tools_list = tools_list
        self.client = self._create_client()

    def _create_client(self) -> OpenRouterClient:
        """Create OpenRouter client with current settings."""
        return OpenRouterClient(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model_name=self.model_name,
            tools_list=self.tools_list,
            temperature=self.temperature
        )

    def set_model(self, model_name: str):
        """Switch to a different model."""
        self.model_name = model_name
        self.client = self._create_client()

    def set_temperature(self, temperature: float):
        """Set temperature for responses."""
        self.temperature = temperature
        self.client = self._create_client()

    def set_tools(self, tools_list: Optional[Iterable]):
        """Update tools available to the model."""
        self.tools_list = tools_list
        self.client = self._create_client()

    def stream_completion(self, messages: list, stream: bool = True):
        """
        Stream a completion from the LLM.

        Args:
            messages: List of message dicts {'role': ..., 'content': ...}
            stream: Whether to stream the response

        Returns:
            Stream of response chunks
        """
        return self.client.create_completions_stream(
            message_list=messages,
            stream=stream
        )
