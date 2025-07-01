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
GEMINI_PRO_25 = 'google/gemini-2.5-pro-preview'
OPENAI_O3 = 'openai/o3'
GPT_4O_2011 = 'openai/gpt-4o-2024-11-20'
GEMINI_FLASH_25 = 'google/gemini-2.5-flash-preview-05-20'
DEEPSEEK_R1_0528 = 'deepseek/deepseek-r1-0528'
GPT_41 = 'openai/gpt-4.1'
DEEPSEEK_V3_0324 = 'deepseek/deepseek-chat-v3-0324'
OPENAI_O4_MINI = 'openai/o4-mini'
DEEPSEEK_R1 = 'deepseek/deepseek-r1'
GEMINI_FLASH_LITE_25 = 'google/gemini-2.5-flash-lite-preview-06-17'
MISTRAL_MEDIUM_2506 = 'mistralai/magistral-medium-2506'
GPT_41_MINI = 'openai/gpt-4.1-mini'
GEMINI_2_FLASH_1 = 'google/gemini-2.0-flash-001'
DEEPSEEK_V3 = 'deepseek/deepseek-chat'
GPT_4O = 'openai/chatgpt-4o'
GPT_4O_LATEST = 'openai/chatgpt-4o-latest'
GPT_4O_MINI = 'openai/gpt-4o-mini-2024-07-18'

# older constants
O3_MINI_HIGH = 'openai/o3-mini-high'
O3_MINI = 'openai/o3-mini'
GEMINI_PRO_15 = 'google/gemini-pro-1.5'
GPT_4O_1305 = 'openai/gpt-4o-2024-05-13'
QWEN_25_PLUS = 'qwen/qwen-plus'
LLAMA_405B_I = 'meta-llama/llama-3.1-405b-instruct'
CLAUDE_35_SONNET_2006 = 'anthropic/claude-3.5-sonnet-20240620'
GEMINI_2_FLASH_LITE = 'google/gemini-2.0-flash-lite-001'
