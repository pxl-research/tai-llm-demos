import copy
import json
import os
import random
import sys

import gradio as gr
from dotenv import load_dotenv

sys.path.append('../../')

from demos.components.open_router_client import OpenRouterClient
from demos.model_choice.or_pricing import get_models

load_dotenv()

system_instruction = {
    'role': 'system',
    'content': 'Be concise. Be precise. Always think step by step. '
               'I would like you to take a deep breath before responding. '
               'You can answer using Markdown syntax if you want to. '
               'When using an external source, always include the reference. '
}

different_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c',
                    '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#aaffc3', '#808000', '#ffd8b1', '#808080']
providers = {}


# blocks UI method
def on_load_ui():
    data_models = get_models(tools_only=False, as_dataframe=True)

    # set precision of price values
    price_columns = data_models.filter(like='price').columns
    format_dict = {col: "{:.3f}".format for col in price_columns}
    format_dict.update({col: "{:.0f}".format for col in ['max_completion_tokens']})

    style_models = (data_models.style
                    .format(format_dict)
                    .map(colorize_quantiles, df=data_models, col='completion_price', subset=['completion_price'])
                    .map(colorize_quantiles, df=data_models, col='prompt_price', subset=['prompt_price'])
                    .map(colorize_contexts, subset=['context_length'])
                    .map(colorize_providers, subset=['provider'])
                    )

    return data_models, style_models


# helper method
def colorize_quantiles(value, df, col):
    if value < df[col].quantile(0.3):
        return 'color:green;'
    if value >= df[col].quantile(0.9):
        return 'color:red;'
    if value > df[col].quantile(0.6):
        return 'color:orange;'
    return ''


def colorize_contexts(context_size):
    if context_size > 64000:
        return 'color:green;'
    if context_size < 10000:
        return 'color:red;'
    if context_size < 20000:
        return 'color:orange;'
    return ''


def colorize_providers(full_model_name):
    provider_name = full_model_name.split('/')[0]

    available_colors = copy.deepcopy(different_colors)
    if provider_name not in providers.keys():
        # select a random color
        color = random.choice(available_colors)
        providers[provider_name] = color
        available_colors.remove(color)

        if len(available_colors) < 1:
            # start re-using these colors when we run out
            available_colors = copy.deepcopy(different_colors)

    return 'color:' + providers[provider_name] + ';'


# blocks UI method
def on_row_selected(select_data: gr.SelectData):
    if select_data is not None:
        return select_data.row_value[1], select_data.row_value[1]  # model name
    return None


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append((user_message, None))
    message_list.append({'role': 'user', 'content': user_message})
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list, model_name):
    yield from complete_with_llm(chat_history, message_list, model_name)


# blocks UI method
def on_clear_clicked():
    # empty the chat log on screen, and the messages internally
    return [None, [system_instruction]]


def complete_with_llm(chat_history, message_list, model_name):
    or_client = OpenRouterClient(model_name=model_name,
                                 api_key=os.getenv('OPENROUTER_API_KEY'))
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
    footer {display:none !important}
"""
with (gr.Blocks(fill_height=True, title='OpenRouter Model Choice', css=custom_css) as llm_client_ui):
    # state
    messages = gr.State([system_instruction])
    selected_model = gr.State('google/gemini-2.0-flash-001')
    df_models = gr.State(None)

    # ui
    cb_live = gr.Chatbot(label='Chat',
                         type='tuples',
                         scale=1,
                         show_copy_button=True)

    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False,
                                 info='Enter your prompt here. Use SHIFT + ENTER to send.',
                                 placeholder='Enter prompt here...',
                                 lines=2,
                                 scale=1)

            btn_send = gr.Button('', scale=0, min_width=64, elem_classes='blue',
                                 icon='../../assets/icons/send.png')
            btn_clear = gr.Button('', scale=0, min_width=64, elem_classes='danger',
                                  icon='../../assets/icons/disposal.png')

        lbl_model = gr.Textbox(label='Currently selected model:',
                               value=selected_model.value,
                               interactive=False,
                               elem_classes='bold')
        with gr.Row():
            with gr.Accordion(label='Available models', open=False):
                dfr_models = gr.DataFrame(df_models.value, type="pandas", interactive=False)

    # event handlers
    tb_user.submit(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, selected_model],
                                     [cb_live, messages])

    btn_send.click(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, selected_model],
                                     [cb_live, messages])

    btn_clear.click(on_clear_clicked,
                    None,
                    [cb_live, messages],
                    queue=False)

    llm_client_ui.load(fn=on_load_ui,
                       inputs=None,
                       outputs=[df_models, dfr_models])
    dfr_models.select(fn=on_row_selected,
                      inputs=[],
                      outputs=[lbl_model, selected_model])

llm_client_ui.queue().launch(auth=None,
                             server_name='0.0.0.0',
                             server_port=7022)
