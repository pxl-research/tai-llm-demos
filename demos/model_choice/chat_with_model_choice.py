import json
import os
import sys

import gradio as gr
import requests
from dotenv import load_dotenv

sys.path.append('../')

from demos.components.open_router_client import OpenRouterClient, GPT_4O_MINI

load_dotenv()

or_client = OpenRouterClient(model_name=GPT_4O_MINI,
                             api_key=os.getenv('OPENROUTER_API_KEY'))

system_instruction = {
    'role': 'system',
    'content': 'Be concise. Be precise. Always think step by step. '
               'I would like you to take a deep breath before responding. '
               'You can answer using Markdown syntax if you want to. '
               'When using an external source, always include the reference. '
}


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append((user_message, None))
    message_list.append({'role': 'user', 'content': user_message})
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list):
    yield from complete_with_llm(chat_history, message_list)


# blocks UI method
def on_load_ui(dd_models):
    models = get_model_list(tools_only=False)

    # large context
    filtered_models = [m for m in models if m['context_length'] >= 100000]

    # affordable price
    filtered_models = [m for m in filtered_models if float(m['pricing']['prompt']) <= 0.000003]
    filtered_models = [m for m in filtered_models if float(m['pricing']['completion']) <= 0.000015]

    model_names = []
    for model in filtered_models:
        ppm_p = float(model['pricing']['prompt']) * 1000000
        ppm_c = float(model['pricing']['completion']) * 1000000
        label = f'{model['name']} - $PM: {ppm_p:.1f} + {ppm_c:.1f}'
        model_names.append((label, model['id']))

    return filtered_models, gr.Dropdown(choices=model_names)


def model_selected(chosen_model):
    print(chosen_model)
    or_client.set_model(chosen_model)


def get_model_list(tools_only=True):
    models_url = 'https://openrouter.ai/api/v1/models'
    if tools_only:
        models_url += '?supported_parameters=tools'
    response = requests.get(models_url)
    response_json = json.loads(response.text)
    models = []
    if 'data' in response_json:
        models = response_json['data']

    # TODO: this sorting feels a bit brittle
    models.sort(key=lambda model: (model['id'].split('/')[0], model['pricing']['completion']))
    return models


def complete_with_llm(chat_history, message_list):
    response_stream = or_client.create_completions_stream(message_list=message_list)

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
    if chat_history[-1][1] is not None:
        message_list.append({'role': 'assistant', 'content': chat_history[-1][1]})

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
        yield from complete_with_llm(chat_history, message_list)


# Gradio UI
custom_css = """
    .danger {background: red;}
    .blue {background: #247BA0;}
"""
with (gr.Blocks(fill_height=True, title='OpenRouter Model Choice', css=custom_css) as llm_client_ui):
    # state
    messages = gr.State([system_instruction])
    model_list = gr.State([])

    # ui
    cb_live = gr.Chatbot(label='Chat', scale=1)

    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False,
                                 placeholder='Enter prompt here...',
                                 lines=3,
                                 scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, elem_classes='blue',
                                 icon='../../assets/icons/send.png')

        with gr.Row():
            dd_models = gr.Dropdown(
                [],
                show_label=False,
                filterable=True,
                info="Select a different model (price per million tokens is shown as '$PM')",
                scale=10,
            )
            btn_clear = gr.Button('', scale=0, min_width=64, elem_classes='danger',
                                  icon='../../assets/icons/disposal.png')

    # event handlers
    tb_user.submit(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_send.click(append_user, [tb_user, cb_live, messages], [tb_user, cb_live, messages],
                   queue=False).then(append_bot, [cb_live, messages], [cb_live, messages])
    btn_clear.click(lambda: None, None, cb_live, queue=False)
    dd_models.input(model_selected, [dd_models], [])

    llm_client_ui.load(on_load_ui, [dd_models], [model_list, dd_models])

llm_client_ui.queue().launch(auth=None, server_name='0.0.0.0', server_port=7897)
