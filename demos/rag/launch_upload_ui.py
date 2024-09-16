import os
import re

import chromadb
import gradio as gr

from fn_chromadb import add_pdf_to_db

# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path='store/')  # on disk


# https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
def sanitize_filename(full_file_path):
    cleaner_name = os.path.basename(full_file_path)  # remove path
    cleaner_name = os.path.splitext(cleaner_name)[0]  # remove extension
    cleaner_name = sanitize_string(cleaner_name)
    return cleaner_name[:60]  # crop it


def sanitize_string(some_text):
    cleaner_name = some_text.strip()
    cleaner_name = cleaner_name.replace(" ", "_")  # spaces to underscores
    cleaner_name = re.sub(r'[^a-zA-Z0-9_-]', '-', cleaner_name)  # replace invalid characters with spaces
    return cleaner_name


def on_file_uploaded(file_list, progress=gr.Progress()):
    # TODO: check if file already in collection?
    for file_path in file_list:
        collection_name = sanitize_filename(file_path)
        add_pdf_to_db(cdb_client, collection_name, file_path, progress)
    names = list_collections()
    return [None, names]


def list_collections():
    collections_list = cdb_client.list_collections()
    names = []
    for collection in collections_list:
        names.append([collection.name])
    return names


def on_remove_rag(file_list, select_data):
    names = []
    if select_data is not None:
        document_name = file_list['Name'][select_data[0]]
        cdb_client.delete_collection(document_name)
        names = list_collections()
    return names, None


def on_row_selected(select_data: gr.SelectData):
    return select_data.index


rag_explainer = (
    'Upload additional information here if you want the language model to be able to perform lookup into it. '
    'Do not upload data files such as spreadsheets or tables; stick to PDF only. '
    'Processing may take considerable time depending on the size of the documents. '
    'Do not interrupt the processing step.')

custom_css = """
    .danger {background: red;}
"""

with gr.Blocks(fill_height=True, title='RAG Upload Demo', css=custom_css) as cdb_demo:
    st_selected_index = gr.State()

    lbl_rag_explainer = gr.Markdown(rag_explainer)

    file_rag_upload = gr.File(label='Click to Upload a File',
                              file_types=['.pdf'],
                              file_count='multiple')

    with gr.Row():
        df_rag_files = gr.Dataframe(label='Collections',
                                    headers=['Name'],
                                    col_count=1,
                                    interactive=False)

        btn_remove_rag_file = gr.Button(value='',
                                        scale=0,
                                        min_width=64,
                                        icon='../../assets/icons/disposal.png',
                                        elem_classes='danger')

    file_rag_upload.upload(on_file_uploaded, [file_rag_upload], [file_rag_upload, df_rag_files])
    df_rag_files.select(on_row_selected, None, [st_selected_index])
    btn_remove_rag_file.click(on_remove_rag, [df_rag_files, st_selected_index], [df_rag_files, st_selected_index])
    cdb_demo.load(list_collections, [], [df_rag_files])

cdb_demo.queue().launch(server_name='0.0.0.0', server_port=7894)
