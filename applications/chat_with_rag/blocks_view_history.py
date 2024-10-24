import json
import os
from datetime import datetime

import gradio as gr

dropdown_entries = []
file_contents = {}
default_folder = "logs/"


def set_folder(user_folder):
    log_folder = f"{default_folder}{user_folder}/"

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    return log_folder


def load_files(log_folder):
    log_folder = os.path.normpath(os.path.abspath(log_folder))
    files = os.listdir(log_folder)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(log_folder, f)), reverse=True)
    entries = []
    for file in files:
        file_path = os.path.normpath(os.path.join(log_folder, file))
        log_file = open(file_path, "r")
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


def remove_file(chosen_file, log_folder):
    full_path = os.path.normpath(f"{log_folder}{chosen_file}")
    print(full_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return load_files(log_folder)
