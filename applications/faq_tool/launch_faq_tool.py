import json
import os
import sys
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

sys.path.append('../../')
from demos.components.open_router_client import OpenRouterClient, GPT_4O_MINI_1807
from demos.tool_calling.tool_descriptors import (tools_rag_descriptor)

# noinspection PyUnresolvedReferences
from tools_rag import lookup_in_documentation

load_dotenv()

custom_headers = {
    'HTTP-Referer': 'https://pxl-digital.be/',
    'X-Title': 'Pixie FAQ Tool'
}

tool_list = [tools_rag_descriptor]
or_client = OpenRouterClient(model_name=GPT_4O_MINI_1807,
                             tools_list=tool_list,
                             api_key=os.getenv('OPENROUTER_API_KEY'),
                             temperature=0.25,
                             custom_headers=custom_headers)

main_topic = 'internships at a university college in Belgium'

system_instruction = {
    'role': 'system',
    'content': 'You are an assistant helping people with information based on documentation. '
               'You should ALWAYS consult your documentation, for every question. '
               'Always include the document reference when using an external source. '
               f'Your area of expertise is {main_topic}. '
               'If you do not know the answer to a question, simply say you do not know. '
               'Only answer questions related to the documentation you are in charge of, '
               'deflect or refrain from answering unrelated queries. '
               'Your responses should never exceed 2000 characters. '
               'I would like you to take a deep breath before responding. '
               'Always think step by step. '
               'Be concise and precise in your responses. '
               'Answer using Markdown syntax when appropriate. '
}


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append((user_message, None))
    message_list.append({'role': 'user', 'content': user_message})
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list, log_file_name):
    yield from complete_with_llm(chat_history, message_list, log_file_name)


def on_clear_clicked():
    return [None, on_load_ui()]


def on_load_ui():
    log_folder = './logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    file_name = datetime.now().strftime('%y%m%d_%H%M%S_%f.log')
    print(f'Started a new log file named "{file_name}"')
    return os.path.join(log_folder, file_name)


def complete_with_llm(chat_history, message_list, log_file_name):
    abbreviated_list = message_list

    # truncate message list for longer chats
    if len(message_list) > 3:
        abbreviated_list = []
        MAX_COUNT = 3
        user_msg_count = 0
        for msg in reversed(message_list):
            if msg['role'] == 'system':
                abbreviated_list.append(msg)
            elif msg['role'] == 'user':
                user_msg_count += 1
                abbreviated_list.append(msg)
            else:
                if user_msg_count < MAX_COUNT:
                    abbreviated_list.append(msg)
                else:
                    if (msg['role'] == 'tool' or
                            (msg['role'] == 'assistant' and 'tool_calls' in msg)):
                        continue  # we skip these
                    else:
                        abbreviated_list.append(msg)
        abbreviated_list.reverse()

    # generate an answer
    response_stream = or_client.create_completions_stream(message_list=abbreviated_list)

    partial_message = ''
    tool_calls = []
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            # LLM text reponses
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
    if chat_history[-1][1] is not None and chat_history[-1][1] != '':
        message_list.append({'role': 'assistant', 'content': chat_history[-1][1]})

        # write to log file
        log_string = json.dumps(message_list, indent=2)
        log_file = open(log_file_name, 'wt')
        log_file.write(log_string)
        log_file.close()

    # handle tool requests
    if len(tool_calls) > 0:
        print(f'Processing {len(tool_calls)} tool calls')
        for call in tool_calls:
            fn_pointer = globals()[call.function.name]
            fn_args = json.loads(call.function.arguments)
            tool_call_obj = {
                'role': 'assistant',
                'content': None,
                'tool_calls': [
                    {
                        'id': call.id,
                        'type': 'function',
                        'function': {
                            'name': call.function.name,
                            'arguments': call.function.arguments
                        }
                    }
                ]
            }
            message_list.append(tool_call_obj)

            if fn_pointer is not None:
                fn_result = fn_pointer(**fn_args)
                tool_resp = {'role': 'tool',
                             'name': call.function.name,
                             'tool_call_id': call.id,
                             'content': json.dumps(fn_result)}
                message_list.append(tool_resp)
        # recursively call completion message to give the LLM a chance to process results
        yield from complete_with_llm(chat_history, message_list, log_file_name)


# Gradio UI
custom_css = """
    footer {display:none !important}
"""
with (gr.Blocks(fill_height=True, title='Pixie FAQ Tool', css=custom_css) as llm_client_ui):
    # state variables
    messages = gr.State([system_instruction])
    log_file_name = gr.State()

    # UI elements
    cb_live = gr.Chatbot(label='Chat', type='tuples', scale=1, show_copy_all_button=True)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False,
                                 placeholder='Enter prompt here...',
                                 max_length=500,
                                 scale=10)
            btn_send = gr.Button('',
                                 icon='../../assets/icons/send.png',
                                 min_width=64,
                                 scale=0)
    btn_clear = gr.Button('Clear')

    # event handlers
    tb_user.submit(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, log_file_name],
                                     [cb_live, messages])

    btn_send.click(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, log_file_name],
                                     [cb_live, messages])

    btn_clear.click(on_clear_clicked, None, [cb_live, log_file_name], queue=False)
    cb_live.clear(on_clear_clicked, None, [cb_live, log_file_name], queue=False)
    llm_client_ui.load(on_load_ui, None, [log_file_name])

llm_client_ui.launch(auth=None, server_name='0.0.0.0', server_port=10000)
