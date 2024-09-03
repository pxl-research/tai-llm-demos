import os

import chromadb
import gradio as gr

from fn_chromadb import add_pdf_to_db

# cdb_client = chromadb.Client()  # in memory
cdb_client = chromadb.PersistentClient(path="store/")  # on disk


# https://docs.trychroma.com/usage-guide#creating-inspecting-and-deleting-collections
def cleanup_filename(full_file_path):
    cleaned_name = os.path.basename(full_file_path)  # remove path
    cleaned_name = os.path.splitext(cleaned_name)[0]  # remove extension
    cleaned_name = cleaned_name.lower()  # lowercase
    cleaned_name = cleaned_name.replace(".", "_")  # no periods
    return cleaned_name[:60]  # crop it


def on_file_uploaded(file_path, progress=gr.Progress()):
    collection_name = cleanup_filename(file_path)
    add_pdf_to_db(cdb_client, collection_name, file_path, progress)
    names = list_collections()
    return [None, names]


def list_collections():
    collections_list = cdb_client.list_collections()
    names = []
    for collection in collections_list:
        names.append([collection.name])
    return names


with gr.Blocks() as cdb_demo:
    file_upload = gr.File(label="Click to Upload a File",
                          file_types=[".pdf"],
                          file_count="single")
    df_files = gr.Dataframe(label="Collections",
                            headers=['Name'],
                            col_count=1,
                            interactive=False)

    file_upload.upload(on_file_uploaded, [file_upload], [file_upload, df_files])
    cdb_demo.load(list_collections, [], [df_files])

cdb_demo.queue().launch(server_name='0.0.0.0', server_port=7894)
