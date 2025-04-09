import gradio as gr
from tqdm import tqdm

from demos.components.vectorstore.vs_utilities import sanitize_filename
from demos.components.vectorstore.chroma_document_store import ChromaDocumentStore

cdb_store = ChromaDocumentStore(path='store/')


def on_file_uploaded(file_list, progress=gr.Progress(track_tqdm=True)):
    current_documents = cdb_store.list_documents()
    for file_path in file_list:
        collection_name = sanitize_filename(file_path)
        if collection_name not in current_documents:
            cdb_store.add_document(file_path, tqdm)

    return [None, wrap_document_list()]


def on_remove_rag(file_list, select_data):
    if select_data is not None:
        document_name = file_list['Name'][select_data[0]]
        cdb_store.remove_document(document_name)
    names = cdb_store.list_documents()
    return names, None


def wrap_document_list():
    doc_list = cdb_store.list_documents()
    wrapped_list = []
    for doc_name in doc_list:
        wrapped_list.append([doc_name])
    return wrapped_list


def on_row_selected(select_data: gr.SelectData):
    return select_data.index


rag_explainer = (
    'Upload additional information here if you want the language model to be able to perform lookup into it. '
    'You can upload documents such as PDFs, Word documents, PowerPoint presentations, and Excel spreadsheets. '
    'Processing may take considerable time depending on the size of the documents. '
    'Do not interrupt the processing step.')

custom_css = """
    .danger {background: red;}
    footer {display:none !important}
"""

with gr.Blocks(fill_height=True, title='RAG Upload Demo', css=custom_css) as cdb_demo:
    st_selected_index = gr.State()

    # UI elements
    lbl_rag_explainer = gr.Markdown(rag_explainer)

    file_rag_upload = gr.File(label='Click to Upload a File',
                              file_types=['.pdf', '.docx', '.pptx', '.xlsx', '.xls'],
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

    # event handlers
    file_rag_upload.upload(on_file_uploaded, [file_rag_upload], [file_rag_upload, df_rag_files])
    df_rag_files.select(on_row_selected, None, [st_selected_index])
    btn_remove_rag_file.click(on_remove_rag, [df_rag_files, st_selected_index], [df_rag_files, st_selected_index])
    cdb_demo.load(wrap_document_list, [], [df_rag_files])

cdb_demo.queue().launch(server_name='0.0.0.0', server_port=7021)
