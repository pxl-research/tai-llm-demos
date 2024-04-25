import gradio as gr

from blocks_llm_chat_with_rag import (
    append_user,
    append_ai,
    clear_log,
    client
)
from blocks_rag_upload import (
    on_file_uploaded,
    list_collections
)
from blocks_view_history import (
    load_files,
    file_selected,
    set_folder,
    remove_file
)
from fn_auth import (
    auth_method
)


def show_live():
    return {
        cb_live: gr.Chatbot(visible=True),
        gr_live: gr.Group(visible=True),
        row_live: gr.Row(visible=True),
        btn_live: gr.Button(interactive=False),

        cb_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False),
        btn_history: gr.Button(interactive=True),

        lbl_explainer: gr.HTML(visible=False),
        file_upload: gr.File(visible=False),
        df_files: gr.Dataframe(visible=False),
        btn_upload: gr.Button(interactive=True)
    }


def show_history():
    return {
        cb_live: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        btn_live: gr.Button(interactive=True),

        cb_history: gr.Chatbot(visible=True),
        gr_history: gr.Group(visible=True),
        btn_history: gr.Button(interactive=False),

        lbl_explainer: gr.HTML(visible=False),
        file_upload: gr.File(visible=False),
        df_files: gr.Dataframe(visible=False),
        btn_upload: gr.Button(interactive=True)
    }


def show_upload():
    return {
        cb_live: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        btn_live: gr.Button(interactive=True),

        cb_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False),
        btn_history: gr.Button(interactive=True),

        lbl_explainer: gr.HTML(visible=True),
        file_upload: gr.File(visible=True),
        df_files: gr.Dataframe(visible=True),
        btn_upload: gr.Button(interactive=False)
    }


def on_login(request: gr.Request):
    user_folder = request.username.strip().lower()
    new_thread = client.beta.threads.create()
    print(f"Created a thread with id: {new_thread.id} for user {user_folder}")
    return [set_folder(user_folder), new_thread]


explainer = (
    'Upload company or business information here if you want the language model to be able to perform lookup into it. '
    'Do not upload data files. Stick to PDF only. '
    'Processing may take considerable time depending on the size of the document. '
    'Do not interrupt the processing step. There is no undo.')

css = """
.danger {background: red;} 
"""

# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with (gr.Blocks(fill_height=True, title='PXL CheaPT', css=css) as llm_client_ui):
    # state that is unique to each user
    log_folder = gr.State("logs/")
    thread = gr.State()

    # live client UI
    cb_live = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send = gr.Button('', scale=0, min_width=64, icon='../assets/icons/send.png')
            btn_remove = gr.Button('', scale=0, min_width=64, icon='../assets/icons/disposal.png')
    with gr.Row() as row_live:
        lbl_debug = gr.HTML('')

        # event handlers
        tb_user.submit(append_user, [tb_user, cb_live], [cb_live]
                       ).then(append_ai, [thread, tb_user, cb_live, log_folder],
                              [tb_user, cb_live, lbl_debug])
        btn_send.click(append_user, [tb_user, cb_live], [cb_live]
                       ).then(append_ai, [thread, tb_user, cb_live, log_folder],
                              [tb_user, cb_live, lbl_debug])
        btn_remove.click(clear_log, [thread], [tb_user, cb_live, thread])

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
            btn_refresh = gr.Button(value='', scale=0, min_width=64, icon='../assets/icons/refresh.png')
            btn_remove = gr.Button(value='', scale=0, min_width=64, icon='../assets/icons/disposal.png',
                                   elem_classes='danger')

        # event handlers
        btn_refresh.click(load_files, [log_folder], [dd_files])
        btn_remove.click(remove_file, [dd_files, log_folder], [dd_files])
        dd_files.input(file_selected, [dd_files], [cb_history])

    # file uppload UI
    lbl_explainer = gr.HTML(explainer, visible=False)
    file_upload = gr.File(label="Click to Upload a File",
                          file_types=[".pdf"],
                          file_count="single",
                          visible=False)
    df_files = gr.Dataframe(label="Collections",
                            headers=['Name'],
                            col_count=1,
                            interactive=False,
                            visible=False,
                            scale=1)

    file_upload.upload(on_file_uploaded, [file_upload], [file_upload, df_files])

    # toggle UI
    with gr.Row():
        btn_live = gr.Button('Chat', icon='../assets/icons/chat.png', interactive=False)
        btn_history = gr.Button('History', icon='../assets/icons/history.png')
        btn_upload = gr.Button('Upload')

        # event handlers
        btn_live.click(show_live, [],
                       [cb_live, gr_live, row_live,
                        cb_history, gr_history,
                        file_upload, df_files, lbl_explainer,
                        btn_live, btn_history, btn_upload])
        btn_history.click(show_history, [],
                          [cb_live, gr_live, row_live,
                           cb_history, gr_history,
                           file_upload, df_files, lbl_explainer,
                           btn_live, btn_history, btn_upload])
        btn_upload.click(show_upload, [],
                         [cb_live, gr_live, row_live,
                          cb_history, gr_history,
                          file_upload, df_files, lbl_explainer,
                          btn_live, btn_history, btn_upload])
    # global event
    llm_client_ui.load(on_login, None, [log_folder, thread])
    llm_client_ui.load(list_collections, [], [df_files])

# To create a public link, set `share=True` in `launch()`.
llm_client_ui.queue().launch(auth=auth_method, server_name='0.0.0.0')
