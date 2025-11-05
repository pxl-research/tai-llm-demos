import json
import os

import gradio as gr
from dotenv import load_dotenv

from demos.components.open_router_client import OpenRouterClient
from demos.tool_calling.descriptors_fileio import tools_fileio_descriptor
from demos.tool_calling.tool_descriptors import (tools_weather_descriptor,
                                                 tools_rag_descriptor,
                                                 tools_search_descriptor,
                                                 tools_get_website_contents)
# noinspection PyUnresolvedReferences
from demos.tool_calling.tools_fileio import (list_files,
                                             get_fs_properties,
                                             read_file_contents,
                                             write_file_contents,
                                             append_file_contents,
                                             create_folders,
                                             delete_file,
                                             delete_folder,
                                             current_working_folder,
                                             get_allowed_folder)
# noinspection PyUnresolvedReferences
from tools_rag import lookup_in_documentation, list_documents
# noinspection PyUnresolvedReferences
from tools_search import search_on_google
# noinspection PyUnresolvedReferences
from tools_surf import (get_webpage_content, get_webpage_with_js)
# noinspection PyUnresolvedReferences
from tools_weather import (get_current_temperature, get_current_rainfall)

load_dotenv()

tool_list = []
tool_list.append(tools_weather_descriptor)  # demo example
tool_list.extend(tools_rag_descriptor)
tool_list.extend(tools_fileio_descriptor)
tool_list.append(tools_search_descriptor)  # requires GOOGLE_API_KEY
tool_list.extend(tools_get_website_contents)

or_client = OpenRouterClient(model_name='anthropic/claude-haiku-4.5',
                             tools_list=tool_list,
                             api_key=os.getenv('OPENROUTER_API_KEY'))

system_instruction = {
    'role': 'system',
    'content': 'Be concise. Be precise. Always think step by step. '
               'I would like you to take a deep breath before responding. '
               'You can answer using Markdown syntax. '
               'You have a lot of tools at your disposal, think about when to use them. '
               'When using an external source, always include the reference. '
}


# blocks UI method
def append_user(user_message, chat_history, message_list):
    msg_obj = {'role': 'user', 'content': user_message}
    chat_history.append(msg_obj)
    message_list.append(msg_obj)
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list):
    yield from complete_with_llm(chat_history, message_list)


def complete_with_llm(chat_history, message_list):
    response_stream = or_client.create_completions_stream(message_list=message_list)

    partial_message = ''
    tool_calls = []
    chat_history.append({'role': 'assistant', 'content': ''})  # append empty response?

    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            # LLM text reponses
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                chat_history[-1]['content'] = partial_message
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
    if chat_history[-1]['content'] is not None:
        message_list.append(chat_history[-1])

    # handle tool requests
    if len(tool_calls) > 0:
        print(f'Processing {len(tool_calls)} tool calls')
        for call in tool_calls:
            print(f'\t- {call.function.name}')
            fn_pointer = globals()[call.function.name]
            if call.function.arguments is not None and len(call.function.arguments) > 0:
                print(f'\t- {call.function.arguments}')
                fn_args = json.loads(call.function.arguments)
            else:
                fn_args = {}
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
        yield from complete_with_llm(chat_history, message_list)


def on_clear_clicked():
    return [None, [system_instruction]]


# Gradio UI
custom_css = """
    footer {display:none !important}
"""
with (gr.Blocks(fill_height=True, title='Tool Calling', css=custom_css) as llm_client_ui):
    messages = gr.State([system_instruction])
    cb_live = gr.Chatbot(label='Chat',
                         type='messages',
                         scale=1,
                         show_copy_button=True)

    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, icon='../../assets/icons/send.png')
    btn_clear = gr.Button('Clear')

    # event handlers
    tb_user.submit(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages],
                                     [cb_live, messages])

    btn_send.click(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages],
                                     [cb_live, messages])

    btn_clear.click(on_clear_clicked,
                    None,
                    [cb_live, messages],
                    queue=False)

llm_client_ui.launch(auth=None, server_name='0.0.0.0', server_port=7023)
