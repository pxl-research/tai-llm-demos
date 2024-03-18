import json
import os

import gradio as gr

log_folder = "logs/"
file_list = []


def load_files(dropdown):
    files = os.listdir(log_folder)
    print(file_list)
    return gr.Dropdown(choices=files)


def file_selected(chosen_file):
    print(chosen_file)
    log_file = open(f"{log_folder}{chosen_file}", "r")
    log_content = log_file.read()

    messages = json.loads(log_content)
    chat_history = []
    for message in messages["data"]:
        if message["role"] == "user" and message["content"][0]["type"] == "text":
            chat_history.append((message["content"][0]["text"]["value"], None))
        elif message["role"] == "assistant" and message["content"][0]["type"] == "text":
            chat_history.append((None, message["content"][0]["text"]["value"]))

    # TODO: load the log into the chat window
    return chat_history


with gr.Blocks(fill_height=True) as log_ui:
    log_box = gr.Chatbot(label='Log', scale=1)
    dd_files = gr.Dropdown(
        file_list,
        label="Log files",
        info="Select a log file to view the details"
    )
    with gr.Row():
        btn_refresh = gr.Button('Reload', scale=1)
        btn_clear = gr.ClearButton([log_box], scale=1)

    btn_refresh.click(load_files, [dd_files], [dd_files])
    dd_files.input(file_selected, [dd_files], [log_box])

log_ui.launch()
