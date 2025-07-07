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
    try:
        files = os.listdir(log_folder)
    except OSError:
        return gr.Dropdown(choices=[])
    files.sort(key=lambda f: os.path.getmtime(os.path.join(log_folder, f)), reverse=True)
    entries = []
    for file in files:
        file_path = os.path.normpath(os.path.join(log_folder, file))
        try:
            with open(file_path, "r") as log_file:
                log_content = log_file.read()
        except (OSError, IOError):
            continue
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
    log_content = file_contents.get(chosen_file)
    if log_content is None:
        return []
    try:
        messages = json.loads(log_content)
    except (json.JSONDecodeError, TypeError):
        return []
    chat_history = []
    for message in messages.get("data", []):
        if message.get("role") == "user":
            chat_history.append({"role": "user", "content": message["content"][0]["text"]["value"]})
        elif message.get("role") == "assistant":
            chat_history.append({"role": "assistant", "content": message["content"][0]["text"]["value"]})
    return chat_history


def remove_file(chosen_file, log_folder):
    full_path = os.path.normpath(f"{log_folder}{chosen_file}")
    print(full_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    return load_files(log_folder)
