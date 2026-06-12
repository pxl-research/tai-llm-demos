from typing import Iterable

from openai import OpenAI


class OpenRouterClient(OpenAI):
    """
    Client for OpenRouter API, supporting streaming completions and tool calling.
    """

    def __init__(self,
                 api_key: str,
                 base_url: str = 'https://openrouter.ai/api/v1',
                 model_name: str = 'anthropic/claude-haiku-4.5',
                 tools_list: Iterable | None = None,
                 temperature: float = 0,
                 custom_headers=None):
        super().__init__(base_url=base_url,
                         api_key=api_key)

        if custom_headers is None:
            custom_headers = {
                'HTTP-Referer': 'https://pxl-research.be/',
                'X-Title': 'PXL Smart ICT'
            }
        self.model_name: str = model_name
        self.tools_list: Iterable | None = tools_list
        self.temperature: float = temperature
        self.extra_headers: dict = custom_headers

    def create_completions_stream(self, message_list: Iterable, stream=True):
        """
        Create a streaming chat completion using the configured model and tools.
        Args:
            message_list: Iterable of message dicts for the chat API.
            stream: Whether to stream the response.
        Returns:
            Streaming response from OpenRouter chat completion.
        """
        extra_body = {}
        if self.tools_list:
            # require_parameters keeps OpenRouter from routing to providers that
            # don't actually support tools (e.g. "Io Net"), which otherwise surface
            # as the cryptic 422 "Provider returned error" mid-stream.
            extra_body['provider'] = {'require_parameters': True}
        return self.chat.completions.create(
            model=self.model_name,
            messages=message_list,
            tools=self.tools_list,
            stream=stream,
            temperature=self.temperature,
            extra_headers=self.extra_headers,
            extra_body=extra_body,
        )

    def set_model(self, model_name: str):
        """
        Set the model name for future completions.
        """
        self.model_name = model_name
