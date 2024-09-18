import gradio as gr

from blocks_llm_chat_with_rag import (
    append_user,
    append_ai,
    clear_chat,
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
from chat_with_rag.blocks_rag_upload import remove_collection
from demos.rag.chroma_document_store import sanitize_string
from fn_auth import (
    auth_method
)


def show_live():
    return {
        cb_live_chat: gr.Chatbot(visible=True),
        gr_live: gr.Group(visible=True),
        row_live: gr.Row(visible=True),
        btn_live: gr.Button(interactive=False),

        cb_chat_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False),
        btn_history: gr.Button(interactive=True),

        lbl_rag_explainer: gr.HTML(visible=False),
        file_rag_upload: gr.File(visible=False),
        df_rag_files: gr.Dataframe(visible=False),
        btn_remove_rag_file: gr.Button(visible=False),
        btn_upload: gr.Button(interactive=True)
    }


def show_history():
    return {
        cb_live_chat: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        btn_live: gr.Button(interactive=True),

        cb_chat_history: gr.Chatbot(visible=True),
        gr_history: gr.Group(visible=True),
        btn_history: gr.Button(interactive=False),

        lbl_rag_explainer: gr.HTML(visible=False),
        file_rag_upload: gr.File(visible=False),
        df_rag_files: gr.Dataframe(visible=False),
        btn_remove_rag_file: gr.Button(visible=False),
        btn_upload: gr.Button(interactive=True)
    }


def show_upload():
    return {
        cb_live_chat: gr.Chatbot(visible=False),
        gr_live: gr.Group(visible=False),
        row_live: gr.Row(visible=False),
        btn_live: gr.Button(interactive=True),

        cb_chat_history: gr.Chatbot(visible=False),
        gr_history: gr.Group(visible=False),
        btn_history: gr.Button(interactive=True),

        lbl_rag_explainer: gr.HTML(visible=True),
        file_rag_upload: gr.File(visible=True),
        df_rag_files: gr.Dataframe(visible=True),
        btn_remove_rag_file: gr.Button(visible=True),
        btn_upload: gr.Button(interactive=False)
    }


def on_login(request: gr.Request):
    user_folder = sanitize_string(request.username.lower())
    new_thread = client.beta.threads.create()
    print(f"Created a thread with id: {new_thread.id} for user {user_folder}")
    return [set_folder(user_folder), new_thread]


def on_remove_rag(file_list, select_data):
    if select_data is not None:
        document_name = file_list['Name'][select_data[0]]
        file_list = remove_collection(document_name)
    return file_list, None


def on_row_selected(select_data: gr.SelectData):
    return select_data.index


rag_explainer = (
    'Upload additional information here if you want the language model to be able to perform lookup into it. '
    'Do not upload data files such as spreadsheets or tables; stick to PDF only. '
    'Processing may take considerable time depending on the size of the documents. '
    'Do not interrupt the processing step.')

custom_css = """
    .danger {background: red;}
    .blue {background: #247BA0;}
    .light_gray {background: #CBD4C2;}
    .dark_gray {background: #50514F;}
    .light_brown {background: #C3B299;}
    footer {display:none !important}
"""

# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with (gr.Blocks(fill_height=True, title='Pixie Lite', css=custom_css) as llm_client_ui):
    # state that is unique to each user
    st_log_folder = gr.State("logs/")
    st_thread = gr.State()
    st_selected_index = gr.State()

    disposal_ico = '../assets/icons/disposal.png'

    # live client UI
    gr.Markdown("## <center>PiXie Lite</center>")
    cb_live_chat = gr.Chatbot(label='Chat', scale=1)
    with gr.Group() as gr_live:
        with gr.Row():
            tb_user_prompt = gr.Textbox(show_label=False, placeholder='Enter prompt here...', scale=10)
            btn_send_prompt = gr.Button('', scale=0, min_width=64, icon='../assets/icons/send.png')
            btn_clear_chat = gr.Button('', scale=0, min_width=64, icon=disposal_ico)
    with gr.Row() as row_live:
        lbl_debug = gr.HTML('')

        # event handlers
        tb_user_prompt.submit(append_user, [tb_user_prompt, cb_live_chat], [cb_live_chat]
                              ).then(append_ai, [st_thread, tb_user_prompt, cb_live_chat, st_log_folder],
                                     [tb_user_prompt, cb_live_chat, lbl_debug])
        btn_send_prompt.click(append_user, [tb_user_prompt, cb_live_chat], [cb_live_chat]
                              ).then(append_ai, [st_thread, tb_user_prompt, cb_live_chat, st_log_folder],
                                     [tb_user_prompt, cb_live_chat, lbl_debug])
        btn_clear_chat.click(clear_chat, [], [tb_user_prompt, cb_live_chat, st_thread])

    # log viewer UI
    cb_chat_history = gr.Chatbot(label='History', scale=1, visible=False)

    with gr.Group(visible=False) as gr_history:
        with gr.Row():
            dd_log_files = gr.Dropdown(
                [],
                show_label=False,
                info="Select a log file to view the details",
                scale=10,
            )
            btn_reload_logs = gr.Button(value='', scale=0, min_width=64, icon='../assets/icons/refresh.png')
            btn_remove_log = gr.Button(value='', scale=0, min_width=64, icon=disposal_ico,
                                       elem_classes='danger')

        # event handlers
        btn_reload_logs.click(load_files, [st_log_folder], [dd_log_files])
        btn_remove_log.click(remove_file, [dd_log_files, st_log_folder], [dd_log_files])
        dd_log_files.input(file_selected, [dd_log_files], [cb_chat_history])

    # file upload UI
    lbl_rag_explainer = gr.HTML(rag_explainer, visible=False)
    file_rag_upload = gr.File(label="Click to Upload a File",
                              file_types=[".pdf"],
                              file_count="multiple",
                              visible=False)
    with gr.Row():
        df_rag_files = gr.Dataframe(label="Documents",
                                    headers=['Name'],
                                    col_count=1,
                                    interactive=False,
                                    visible=False,
                                    scale=1)
        btn_remove_rag_file = gr.Button(value='',
                                        scale=0,
                                        min_width=64,
                                        icon=disposal_ico,
                                        elem_classes='danger',
                                        visible=False)

    file_rag_upload.upload(on_file_uploaded, [file_rag_upload], [file_rag_upload, df_rag_files])
    df_rag_files.select(on_row_selected, None, [st_selected_index])
    btn_remove_rag_file.click(on_remove_rag, [df_rag_files, st_selected_index], [df_rag_files, st_selected_index])

    # toggle different UI modes
    with gr.Row():
        btn_live = gr.Button('Chat', icon='../assets/icons/chat.png', interactive=False, elem_classes='blue')
        btn_history = gr.Button('History', icon='../assets/icons/history.png', elem_classes='light_gray')
        btn_upload = gr.Button('Upload', icon='../assets/icons/upload.png', elem_classes='light_brown')

        # event handlers
        btn_live.click(show_live, [],
                       [cb_live_chat, gr_live, row_live,
                        cb_chat_history, gr_history,
                        file_rag_upload, df_rag_files, lbl_rag_explainer, btn_remove_rag_file,
                        btn_live, btn_history, btn_upload])
        btn_history.click(show_history, [],
                          [cb_live_chat, gr_live, row_live,
                           cb_chat_history, gr_history,
                           file_rag_upload, df_rag_files, lbl_rag_explainer, btn_remove_rag_file,
                           btn_live, btn_history, btn_upload])
        btn_upload.click(show_upload, [],
                         [cb_live_chat, gr_live, row_live,
                          cb_chat_history, gr_history,
                          file_rag_upload, df_rag_files, lbl_rag_explainer, btn_remove_rag_file,
                          btn_live, btn_history, btn_upload])
    # global event
    llm_client_ui.load(on_login, None, [st_log_folder, st_thread])
    llm_client_ui.load(list_collections, [], [df_rag_files])

# To create a public link, set `share=True` in `launch()`.
llm_client_ui.queue().launch(auth=auth_method, server_name='0.0.0.0', server_port=7898)
