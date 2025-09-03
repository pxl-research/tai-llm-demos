import json
import os
import sys
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

sys.path.append('../../')
from demos.components.open_router_client import OpenRouterClient, GPT_4O_MINI
from demos.tool_calling.tool_descriptors import (tools_rag_descriptor)

# noinspection PyUnresolvedReferences
from tools_rag import lookup_in_documentation, list_documents

load_dotenv()

custom_headers = {
    'HTTP-Referer': 'https://pxl-digital.be/',
    'X-Title': 'Pixie FAQ Tool'
}

tool_list = tools_rag_descriptor
or_client = OpenRouterClient(model_name=GPT_4O_MINI,
                             tools_list=tool_list,
                             api_key=os.getenv('OPENROUTER_API_KEY'),
                             temperature=0.25,
                             custom_headers=custom_headers)

main_topic = 'internships at PXL University College in Belgium'

system_instruction = {
    'role': 'system',
    'content': 'You are an assistant helping people with information based on documentation. '
               f'Your area of expertise is "{main_topic}". '
               'Always consult your documentation, do this for every question you get. '
               'Always include the source (document name, page, paragraph, ...) when using the documentation. '
               'If you do not know the answer to a question, simply say that you do not know. '
               'Only answer questions related to the documentation you are in charge of, '
               'deflect or refrain from answering unrelated queries. '
               'Your responses should never exceed 2000 characters. '
               'I would like you to take a deep breath before responding. '
               'Always think step by step. '
               'Be complete, precise and concise in your responses. '
               'Answer using Markdown syntax when appropriate. '
}


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append({'role': 'user', 'content': user_message})
    message_list.append({'role': 'user', 'content': user_message})
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list, log_file_name):
    yield from complete_with_llm(chat_history, message_list, log_file_name)


def on_clear_clicked():
    return [None, on_load_ui(), [system_instruction]]


def on_load_ui():
    log_folder = './logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    file_name = datetime.now().strftime('%y%m%d_%H%M%S_%f.log')
    print(f'Started a new log file named "{file_name}"')
    return os.path.join(log_folder, file_name)


def complete_with_llm(chat_history, message_list, log_file_name):
    # generate an answer
    response_stream = or_client.create_completions_stream(message_list=message_list)

    partial_message = ''
    tool_calls = []

    chat_history.append({'role': 'assistant', 'content': ''})

    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            # LLM text reponses
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                if partial_message:  # Check if partial_message is not empty
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
    if chat_history[-1]['content'] is not None and chat_history[-1]['content'] != '':
        message_list.append({'role': 'assistant', 'content': chat_history[-1]['content']})

        # write to log file
        log_string = json.dumps(message_list, indent=2)
        log_file = open(log_file_name, 'wt')
        log_file.write(log_string)
        log_file.close()

    # handle tool requests
    if len(tool_calls) > 0:
        print(f'Processing {len(tool_calls)} tool calls')
        for call in tool_calls:
            print(f'\t- {call.function.name}')
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
    
    .bg-gold {background: #ae9a64}
    .fg-gold {color: #ae9a64}
    
    :root {
      --color-accent-soft: #f7f5ef;
      --border-color-accent-subdued: #ae9a64;
      --border-color-primary: #dfd7c1;
    }
"""

feedback_message = (
    f'*If you encounter any problems or bugs, '
    f'please drop us a line at <{os.getenv('FEEDBACK_EMAIL')}>! '
    f'Don\'t forget to include a screenshot of a copy of your chatlog.*')

concurrency_limit = 10

with (gr.Blocks(fill_height=True, title='Pixie FAQ Tool', css=custom_css) as llm_client_ui):
    # state variables
    messages = gr.State([system_instruction])
    log_file_name = gr.State()

    # UI elements
    cb_live = gr.Chatbot(label='Chat',
                         type='messages',
                         scale=1,
                         show_copy_button=True)

    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False,
                                 placeholder='Enter prompt here...',
                                 max_length=500,
                                 scale=10)
            btn_send = gr.Button('',
                                 icon='../../assets/icons/send.png',
                                 elem_classes='bg-gold',
                                 min_width=64,
                                 scale=0)

    btn_clear = gr.Button('Clear',
                          elem_classes='fg-gold')
    lbl_feedback = gr.Markdown(feedback_message)

    # event handlers
    tb_user.submit(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   concurrency_limit=concurrency_limit).then(append_bot,
                                                             [cb_live, messages, log_file_name],
                                                             [cb_live, messages])

    btn_send.click(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   concurrency_limit=concurrency_limit).then(append_bot,
                                                             [cb_live, messages, log_file_name],
                                                             [cb_live, messages])

    btn_clear.click(on_clear_clicked, None,
                    [cb_live, log_file_name, messages],
                    concurrency_limit=concurrency_limit)
    cb_live.clear(on_clear_clicked, None,
                  [cb_live, log_file_name, messages],
                  concurrency_limit=concurrency_limit)
    llm_client_ui.load(on_load_ui, None,
                       [log_file_name])

llm_client_ui.launch(auth=None,
                     server_name='0.0.0.0',
                     server_port=10000)
