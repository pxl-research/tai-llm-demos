import json
import os
import time

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OPENROUTER_ENDPOINT"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

system_instruction = {
    "role": "system",
    "content": "Be concise. Be precise. "
               "I would like you to take a deep breath before responding. "
               "Always think step by step. "
}

log_filename = None
previous_history = ''


def get_new_filename(log_folder):
    ts_in_secs = round(time.time())
    return f"{log_folder}{ts_in_secs}.json"


def store_history(history, log_folder):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    global log_filename
    global previous_history

    current_history = json.dumps(history, indent=1)

    if log_filename is None or not current_history.startswith(previous_history[:-2]):
        # this is a new thread -> start a new log
        log_filename = get_new_filename(log_folder)

    log_file = open(log_filename, "wt")
    log_file.write(current_history)
    log_file.close()

    previous_history = current_history


def predict(message, history):
    history_openai_format = [system_instruction]  # openai format

    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    # call the language model
    response_stream = client.chat.completions.create(model="openai/gpt-4o-mini",
                                                     messages=history_openai_format,
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

    # store in a log file
    history_openai_format.append({"role": "assistant", "content": partial_message})
    store_history(history_openai_format, "logs/")


# https://www.gradio.app/guides/creating-a-chatbot-fast
gr.ChatInterface(predict).launch(server_name="0.0.0.0", server_port=7020)
