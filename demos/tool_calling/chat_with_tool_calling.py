import json
import os
import time

import gradio as gr
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

system_instruction = {
    "role": "system",
    "content": "Be concise. Be precise. "
               "I would like you to take a deep breath before responding. "
               "Always think step by step. "
}

tools = [{
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ]
                }
            },
            "required": [
                "location"
            ]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "get_current_rainfall",
            "description": "Get the current rainfall in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit"
                        ]
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]


def get_current_temperature(location, unit="Celsius"):
    return {"temp": "30 degrees celsius"}


def get_current_rainfall(location, unit="mm"):
    return {"rainfall": "10mm"}


def store_history(history, log_folder):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    timestamp = time.time()
    log_file = open(f"{log_folder}{timestamp}.json", "w")
    content = json.dumps(history, indent=1)
    log_file.write(content)
    log_file.close()


def predict(message, history):
    history_openai_format = [system_instruction]  # openai format

    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    # call the language model
    response_stream = client.chat.completions.create(model='openai/gpt-4o-mini',
                                                     messages=history_openai_format,
                                                     tools=tools,
                                                     extra_headers={
                                                         "HTTP-Referer": "PXL University College",
                                                         "X-Title": "basic_chat.py"
                                                     },
                                                     stream=True)
    partial_message = ""
    tool_calls = []
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                yield partial_message

            # https://community.openai.com/t/has-anyone-managed-to-get-a-tool-call-working-when-stream-true/498867/10
            if chunk.choices[0].delta.tool_calls is not None:
                for tool_call_chunk in chunk.choices[0].delta.tool_calls:
                    if tool_call_chunk.index >= len(tool_calls):
                        tool_calls.insert(tool_call_chunk.index, tool_call_chunk)
                    else:
                        if tool_call_chunk.function is not None:
                            if tool_calls[tool_call_chunk.index].function is None:
                                tool_calls[tool_call_chunk.index].function = tool_call_chunk.function
                            else:
                                tool_calls[
                                    tool_call_chunk.index].function.arguments += tool_call_chunk.function.arguments

    for call in tool_calls:
        print(call)
        fn_pointer = globals()[call.function.name]
        fn_args = json.loads(call.function.arguments)
        if fn_pointer is not None:
            fn_result = fn_pointer(**fn_args)
            print(fn_result)

    # store in a log file
    history_openai_format.append({"role": "assistant", "content": partial_message})
    store_history(history_openai_format, 'logs/')

    # cost estimate
    rate = 1667000  # in tokens per dollar
    tokeniser = tiktoken.encoding_for_model("gpt-4")
    hist_string = json.dumps(history_openai_format)
    hist_len = len(tokeniser.encode(hist_string))
    cost_in_dollar_cents = round(hist_len / rate * 1000, ndigits=2)
    print(f"Cost estimate: {cost_in_dollar_cents} cents for history of {hist_len} tokens")


# https://www.gradio.app/guides/creating-a-chatbot-fast
gr.ChatInterface(predict).launch(server_name='0.0.0.0', server_port=7896)
