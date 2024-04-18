import json
import os
from datetime import datetime

import gradio as gr

dropdown_entries = []
file_contents = {}
default_folder = "logs/"
log_folder = default_folder # TODO this is a bug, should be gr.State instead of global var


def set_folder(request: gr.Request):
    global log_folder
    user_folder = request.username.strip().lower()
    log_folder = f"{default_folder}{user_folder}/"
    return None


def get_folder():
    return log_folder


def load_files():
    files = os.listdir(log_folder)
    files.sort(key=lambda f: os.path.getmtime(f"{log_folder}{f}"), reverse=True)
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
    log_content = file_contents[chosen_file]
    messages = json.loads(log_content)

    chat_history = []
    for message in messages["data"]:
        if message["role"] == "user" and message["content"][0]["type"] == "text":
            chat_history.append((message["content"][0]["text"]["value"], None))
        elif message["role"] == "assistant" and message["content"][0]["type"] == "text":
            chat_history.append((None, message["content"][0]["text"]["value"]))

    return chat_history


def remove_file(chosen_file):
    full_path = f"{log_folder}{chosen_file}"
    print(full_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return load_files()


with gr.Blocks(fill_height=True, title='Chat history') as history_ui:
    log_box = gr.Chatbot(label='History', scale=1)

    with gr.Group():
        with gr.Row():
            dd_files = gr.Dropdown(
                dropdown_entries,
                show_label=False,
                info="Select a log file to view the details",
                scale=10
            )
            btn_refresh = gr.Button('Reload', scale=0, min_width=64)
            btn_remove = gr.ClearButton([log_box], scale=0, min_width=64)

    btn_refresh.click(load_files, [], [dd_files])
    dd_files.input(file_selected, [dd_files], [log_box])

# history_ui.launch()
