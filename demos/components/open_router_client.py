from typing import Iterable

from openai import OpenAI


class OpenRouterClient(OpenAI):
    model_name: str
    tools_list: list
    temperature: float

    def __init__(self,
                 api_key: str,
                 base_url: str = 'https://openrouter.ai/api/v1',
                 model_name: str = 'openai/gpt-4o-mini',
                 tools_list: list = None,
                 temperature: float = 0,
                 custom_headers=None):
        super().__init__(base_url=base_url,
                         api_key=api_key)

        if custom_headers is None:
            custom_headers = {
                'HTTP-Referer': 'https://pxl-research.be/',
                'X-Title': 'PXL Smart ICT'
            }
        self.model_name = model_name
        self.tools_list = tools_list
        self.temperature = temperature
        self.extra_headers = custom_headers

    def create_completions_stream(self, message_list: Iterable, stream=True):
        return self.chat.completions.create(model=self.model_name,
                                            messages=message_list,
                                            tools=self.tools_list,
                                            stream=stream,
                                            temperature=self.temperature,
                                            extra_headers=self.extra_headers)

    def set_model(self, model_name: str):
        self.model_name = model_name


# some models with tool calling (sorted from more to less powerful)
GEMINI_2_FLASH_1 = 'google/gemini-2.0-flash-001'
QWEN_25_MAX = 'qwen/qwen-max'
O3_MINI_HIGH = 'openai/o3-mini-high'
GPT_41_MINI = 'openai/gpt-4.1-mini'
DEEPSEEK_V3 = 'deepseek/deepseek-chat'
O3_MINI = 'openai/o3-mini'
GEMINI_PRO_15 = 'google/gemini-pro-1.5'
GPT_4O_1305 = 'openai/gpt-4o-2024-05-13'
QWEN_25_PLUS = 'qwen/qwen-plus'
DEEPSEEK_V25 = 'deepseek/deepseek-chat-v2.5'
GPT_4O_MINI_1807 = 'openai/gpt-4o-mini-2024-07-18'
NEMOTRON_70B_I = 'nvidia/llama-3.1-nemotron-70b-instruct'
LLAMA_405B_I = 'meta-llama/llama-3.1-405b-instruct'
CLAUDE_35_SONNET_2006 = 'anthropic/claude-3.5-sonnet-20240620'
GEMINI_2_FLASH_LITE = 'google/gemini-2.0-flash-lite-001'
