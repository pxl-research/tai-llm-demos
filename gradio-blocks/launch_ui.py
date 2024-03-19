import gradio as gr

from blocks import (
    append_user,
    append_ai,
    clear_log
)
from logviewer import (
    load_files,
    file_selected
)


def show_live():
    return {
        cb_live: gr.Chatbot(visible=True),
        gr_live: gr.Group(visible=True),
        row_live: gr.Row(visible=True),
        cb_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False)
    }


def show_history():
    return {
        cb_live: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        cb_history: gr.Chatbot(visible=True),
        gr_history: gr.Group(visible=True),
    }


with gr.Blocks(fill_height=True, title='PXL CheaPT') as llm_client_ui:
    # live client UI
    cb_live = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('Send', scale=0, min_width=64)
            btn_clear = gr.Button('Clear', scale=0, min_width=64)
    with gr.Row() as row_live:
        lbl_debug = gr.HTML()

    # event handlers
    tb_user.submit(append_user, [tb_user, cb_live], [cb_live]
                   ).then(append_ai, [tb_user, cb_live], [tb_user, cb_live, lbl_debug])
    btn_send.click(append_user, [tb_user, cb_live], [cb_live]
                   ).then(append_ai, [tb_user, cb_live], [tb_user, cb_live, lbl_debug])
    btn_clear.click(clear_log, None, [tb_user, cb_live])

    # log viewer UI
    cb_history = gr.Chatbot(label='History', scale=1, visible=False)

    with gr.Group(visible=False) as gr_history:
        with gr.Row():
            dd_files = gr.Dropdown(
                [],
                show_label=False,
                info="Select a log file to view the details",
                scale=10
            )
            btn_refresh = gr.Button('Reload', scale=0, min_width=64)
            btn_clear = gr.ClearButton([cb_history], scale=0, min_width=64)

    # event handlers
    btn_refresh.click(load_files, [dd_files], [dd_files])
    dd_files.input(file_selected, [dd_files], [cb_history])

    # toggle UI
    with gr.Row():
        btn_live = gr.Button('Chat')
        btn_history = gr.Button('History')

    # event handlers
    btn_live.click(show_live, [], [cb_live, gr_live, row_live, cb_history, gr_history])
    btn_history.click(show_history, [], [cb_live, gr_live, row_live, cb_history, gr_history])

llm_client_ui.launch()
