import json
import os

import gradio as gr
import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv('AOA_API_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AOA_ENDPOINT'),
)

system_instruction = {
    'role': 'system',
    'content': 'Be concise. Be precise. '
               'I would like you to take a deep breath before responding. '
               'Always think step by step. '
}


def chat_completion(message, history):
    # token estimation
    tokeniser = tiktoken.encoding_for_model('gpt-4')
    msg_len = len(tokeniser.encode(message))
    print(f'Message: {message} ({msg_len} tokens)')

    if system_instruction not in history:
        # prepend system instructions
        history.insert(0, system_instruction)

    # append latest prompt
    history.append({'role': 'user', 'content': message})

    # clean up extra fields
    for event in history:
        for key in list(event):
            if key == 'role' or key == 'content':
                continue
            else:
                del event[key]

    # token estimation
    hist_string = json.dumps(history)
    hist_len = len(tokeniser.encode(hist_string))
    print(f'History: {hist_len} tokens')

    # cost estimation
    cost_in_cents = round(hist_len / 1000 * 3)
    if cost_in_cents > 0:
        print(f'Cost estimate: {cost_in_cents} cents')

    response_stream = client.chat.completions.create(model='gpt-4o-mini',
                                                     messages=history,
                                                     temperature=1.0,
                                                     stream=True)
    partial_message = ''
    for chunk in response_stream:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message


# https://www.gradio.app/guides/creating-a-chatbot-fast
(gr.ChatInterface(chat_completion, type='messages')
 .launch(server_name='0.0.0.0', server_port=7020))
