import json
import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from tools_weather import (tools_weather, get_current_temperature, get_current_rainfall)

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


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append((user_message, None))
    message_list.append({"role": "user", "content": user_message})
    return "", chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list):
    yield from complete_with_llm(chat_history, message_list)


def complete_with_llm(chat_history, message_list):
    response_stream = client.chat.completions.create(model='openai/gpt-4o-mini',
                                                     messages=message_list,
                                                     tools=tools_weather,
                                                     extra_headers={
                                                         "HTTP-Referer": "https://pxl-research.be/",
                                                         "X-Title": "PXL Smart ICT"
                                                     },
                                                     stream=True)

    partial_message = ""
    tool_calls = []
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            # LLM reponses
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                chat_history[-1][1] = partial_message
                yield chat_history, message_list

            # LLM tool call requests
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

    response_stream.close()

    # handle text responses
    if chat_history[-1][1] is not None:
        message_list.append({"role": "assistant", "content": chat_history[-1][1]})

    # handle tool requests
    if len(tool_calls) > 0:
        print(f'Processing {len(tool_calls)} tool calls')
        for call in tool_calls:
            fn_pointer = globals()[call.function.name]
            fn_args = json.loads(call.function.arguments)
            tool_call_obj = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                ]
            }
            message_list.append(tool_call_obj)

            if fn_pointer is not None:
                fn_result = fn_pointer(**fn_args)
                tool_resp = {"role": "tool",
                             "name": call.function.name,
                             "tool_call_id": call.id,
                             "content": json.dumps(fn_result)}
                message_list.append(tool_resp)
        # recursively call completion message to give the LLM a chance to process results
        yield from complete_with_llm(chat_history, message_list)


# Gradio UI
# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with (gr.Blocks(fill_height=True, title='Tool Calling') as llm_client_ui):
    messages = gr.State([system_instruction])
    cb_live = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, icon='../../assets/icons/send.png')
    btn_clear = gr.Button("Clear")

    # event handlers
    tb_user.submit(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_send.click(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_clear.click(lambda: None, None, cb_live, queue=False)

llm_client_ui.launch(auth=None, server_name='0.0.0.0', server_port=7896)
