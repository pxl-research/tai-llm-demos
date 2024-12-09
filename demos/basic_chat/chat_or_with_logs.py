import datetime
import json
import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv('OPENROUTER_ENDPOINT'),
    api_key=os.getenv('OPENROUTER_API_KEY'),
)

system_instruction = {
    'role': 'system',
    'content': 'Be concise. Be precise. '
               'I would like you to take a deep breath before responding. '
               'Always think step by step. '
}

log_filename = None
previous_history = ''


def get_new_filename(log_folder):
    time_stamp = f'{datetime.datetime.now():%y%m%d_%H%M_%S}'
    return f'{log_folder}{time_stamp}.json'


def store_history(history, log_folder):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    global log_filename
    global previous_history

    for event in history:
        if 'metadata' in event:
            del event['metadata']

    current_history = json.dumps(history, indent=1)

    if log_filename is None or not current_history.startswith(previous_history[:-2]):
        # this is a new thread -> start a new log
        log_filename = get_new_filename(log_folder)

    log_file = open(log_filename, 'wt')
    log_file.write(current_history)
    log_file.close()

    previous_history = current_history


def chat_completion(message, history):
    if system_instruction not in history:
        # prepend system instructions
        history.insert(0, system_instruction)

    # append latest prompt
    history.append({'role': 'user', 'content': message})

    # call the language model
    response_stream = client.chat.completions.create(model='openai/gpt-4o-mini',
                                                     messages=history,
                                                     extra_headers={
                                                         'HTTP-Referer': 'https://pxl-research.be/',
                                                         'X-Title': 'PXL Smart ICT'
                                                     },
                                                     stream=True)
    partial_message = ''
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message

    # store in a log file
    history.append({'role': 'assistant', 'content': partial_message})
    store_history(history, 'logs/')


# https://www.gradio.app/guides/creating-a-chatbot-fast
(gr.ChatInterface(chat_completion, type='messages')
 .launch(server_name='0.0.0.0', server_port=7020))
