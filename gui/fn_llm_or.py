import json
import os

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=".env")


class OpenLLM:
    client = None
    history = None

    # constructor
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_ENDPOINT"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        # openai format
        system_instruction = {
            "role": "system",
            "content": "Be concise. Be precise. "
                       "I would like you to take a deep breath before responding. "
                       "Always think step by step. "
        }

        self.history = [system_instruction]

    def complete(self, prompt):
        self.history.append({"role": "user", "content": prompt})

        # call the language model
        response_stream = self.client.chat.completions.create(model='openai/gpt-4o-mini',
                                                              messages=self.history,
                                                              extra_headers={
                                                                  "HTTP-Referer": "https://pxl-research.be/",
                                                                  "X-Title": "PXL Smart ICT"
                                                              },
                                                              stream=True)
        partial_message = ""
        for chunk in response_stream:  # stream the response
            if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                yield partial_message

        # append to history
        self.history.append({"role": "assistant", "content": partial_message})

        # cost estimate
        rate = 1667000  # in tokens per dollar
        tokeniser = tiktoken.encoding_for_model("gpt-4")
        hist_string = json.dumps(self.history)
        hist_len = len(tokeniser.encode(hist_string))
        cost_in_dollar_cents = round(hist_len / rate * 1000, ndigits=2)
        print(f"Cost estimate: {cost_in_dollar_cents} cents for history of {hist_len} tokens")

    def get_history(self):
        return self.history
