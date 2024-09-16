import os
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenRouterClient(OpenAI):
    model_name: str
    tools_list: list
    extra_headers = {
        'HTTP-Referer': 'https://pxl-research.be/',
        'X-Title': 'PXL Smart ICT'
    }

    def __init__(self,
                 base_url: str = 'https://openrouter.ai/api/v1',
                 api_key: str = os.getenv('OPENROUTER_API_KEY'),
                 model_name: str = 'openai/gpt-4o-mini',
                 tools_list: list = None):
        super().__init__(base_url=base_url,
                         api_key=api_key)

        self.model_name = model_name
        self.tools_list = tools_list

    def create_completions_stream(self, message_list: Iterable):
        return self.chat.completions.create(model=self.model_name,
                                            messages=message_list,
                                            tools=self.tools_list,
                                            extra_headers=self.extra_headers,
                                            stream=True)
