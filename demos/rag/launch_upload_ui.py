import sys

import gradio as gr
from tqdm import tqdm

sys.path.append('../../')

from components.text_utils.md_chunking import iterative_chunking
from components.text_utils.md_conversion import document_to_markdown
from components.text_utils.string_utils import sanitize_filename
from components.vectorstore.chroma_document_store import ChromaDocumentStore

cdb_store = ChromaDocumentStore(path='store/')


def on_file_uploaded(file_list, progress=gr.Progress(track_tqdm=True)):
    current_documents = cdb_store.list_documents()
    for file_path in file_list:
        collection_name = sanitize_filename(file_path)
        if collection_name not in current_documents:
            md_text = document_to_markdown(file_path)
            chunks = iterative_chunking(md_text)
            meta_info = [{'source': file_path, 'id': f'chunk_{i}'} for i in range(len(chunks))]
            cdb_store.add_document(document_name=collection_name,
                                   chunks=chunks,
                                   meta_infos=meta_info,
                                   tqdm_func=tqdm)

    return None, refresh_document_choices()


def on_remove_rag(selected_name):
    if selected_name is not None:
        cdb_store.remove_document(selected_name)
    return refresh_document_choices()


def refresh_document_choices():
    return gr.Radio(choices=cdb_store.list_documents(), value=None)


rag_explainer = (
    'Upload additional information here if you want the language model to be able to perform lookup into it. '
    'You can upload documents such as PDFs, Word documents, PowerPoint presentations, and Excel spreadsheets. '
    'Processing may take considerable time depending on the size of the documents. '
    'Do not interrupt the processing step.')

custom_css = """
    .danger {background: red;}
    footer {display:none !important}
"""

with gr.Blocks(fill_height=True, title='RAG Upload Demo') as cdb_demo:
    # UI elements
    lbl_rag_explainer = gr.Markdown(rag_explainer)

    file_rag_upload = gr.File(label='Click to Upload a File',
                              file_types=['.pdf', '.docx', '.pptx', '.xlsx', '.xls'],
                              file_count='multiple')

    with gr.Row(scale=1):
        rd_rag_files = gr.Radio(label='Collections')

        btn_remove_rag_file = gr.Button(value='',
                                        scale=0,
                                        min_width=64,
                                        icon='../../assets/icons/disposal.png',
                                        elem_classes='danger')

    # event handlers
    file_rag_upload.upload(on_file_uploaded, [file_rag_upload], [file_rag_upload, rd_rag_files])
    btn_remove_rag_file.click(on_remove_rag, [rd_rag_files], [rd_rag_files])
    cdb_demo.load(refresh_document_choices, [], [rd_rag_files])

cdb_demo.queue().launch(server_name='0.0.0.0', server_port=7021, css=custom_css)
