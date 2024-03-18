import json
import os
from datetime import datetime

import gradio as gr

log_folder = "logs/"
dropdown_entries = []
file_contents = {}


def load_files(dropdown):
    files = os.listdir(log_folder)
    entries = []
    for file in files:
        log_file = open(f"{log_folder}{file}", "r")
        log_content = log_file.read()
        file_contents[file] = log_content
        title = get_title(log_content, file)
        entries.append((title, file))

    return gr.Dropdown(choices=entries)


def get_title(log_content, default_title=""):
    title = default_title
    messages = json.loads(log_content)
    if messages["data"] and len(messages["data"]) > 0:
        first_message = messages["data"][0]
        if first_message["created_at"]:
            date_obj = datetime.fromtimestamp(first_message["created_at"])
            title = f"[{date_obj}]"
        if first_message["content"] and len(first_message["content"]) > 0:
            first_content = first_message["content"][0]
            if first_content["type"] == "text":
                first_text = first_content['text']['value'][:100]
                title = f"{title} {first_text}..."
    return title


def file_selected(chosen_file):
    print(chosen_file)
    log_content = file_contents[chosen_file]

    messages = json.loads(log_content)
    chat_history = []
    for message in messages["data"]:
        if message["role"] == "user" and message["content"][0]["type"] == "text":
            chat_history.append((message["content"][0]["text"]["value"], None))
        elif message["role"] == "assistant" and message["content"][0]["type"] == "text":
            chat_history.append((None, message["content"][0]["text"]["value"]))

    # TODO: load the log into the chat window
    return chat_history


with gr.Blocks(fill_height=True, title='Log Viewer') as log_ui:
    log_box = gr.Chatbot(label='Log', scale=1)
    dd_files = gr.Dropdown(
        dropdown_entries,
        label="Log files",
        info="Select a log file to view the details"
    )
    with gr.Row():
        btn_refresh = gr.Button('Reload', scale=1)
        btn_clear = gr.ClearButton([log_box], scale=1)

    btn_refresh.click(load_files, [dd_files], [dd_files])
    dd_files.input(file_selected, [dd_files], [log_box])

log_ui.launch()
