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
GPT_4O_LATEST = 'openai/chatgpt-4o-latest'
GEMINI_PRO_15 = 'google/gemini-pro-1.5',
GPT_O1_MINI = 'openai/o1-mini'
GPT_4O_1305 = 'openai/gpt-4o-2024-05-13'
CLAUDE_35_SONNET_2006 = 'anthropic/claude-3.5-sonnet-20240620'
LLAMA_405B_I = 'meta-llama/llama-3.1-405b-instruct',
GPT_4O_0608 = 'openai/gpt-4o-2024-08-06',
GPT_4O_MINI_1807 = 'openai/gpt-4o-mini-2024-07-18'
GEMINI_FLASH_15 = 'google/gemini-flash-1.5',
NEMOTRON_70B_I = 'nvidia/llama-3.1-nemotron-70b-instruct'
GPT_4O_MINI = 'openai/gpt-4o-mini',
QWEN_25_72B_I = 'qwen/qwen-2.5-72b-instruct'
MISTRAL_LARGE_07 = 'mistralai/mistral-large-2407'
LLAMA_31_70B_I = 'meta-llama/llama-3.1-70b-instruct',
JAMBA_LARGE = 'ai21/jamba-1-5-large'
GEMMA_2_72B = 'google/gemma-2-27b-it'
YI_LARGE = '01-ai/yi-large'
LLAMA_3_70B_I = 'meta-llama/llama-3-70b-instruct'
CLAUDE_3_SONNET = 'anthropic/claude-3-sonnet'
CLAUDE3_HAIKU = 'anthropic/claude-3-haiku',
JAMBA_MINI = 'ai21/jamba-1-5-mini',
LLAMA_8B_I = 'meta-llama/llama-3.1-8b-instruct',
