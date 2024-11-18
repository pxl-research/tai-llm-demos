import re

import pymupdf


def pdf_to_text(filename):
    page_list = []

    doc_reader = pymupdf.open(filename)
    for page in doc_reader:
        page_text = page.get_text()  # convert page from pdf to text
        page_list.append(page_text)
    return page_list


def bigger_chunks(chunk_list, min_size):
    bigger_chunk_list = []

    current_chunk = ''
    for chunk in chunk_list:
        chunk = chunk.strip()
        if len(current_chunk) < min_size:  # too small
            current_chunk = f"{current_chunk}.\n{chunk}"  # stick together
        else:  # big enough
            bigger_chunk_list.append(current_chunk)  # add to list
            current_chunk = chunk  # start with next chunk

    bigger_chunk_list.append(current_chunk)  # append last chunk

    return bigger_chunk_list


def pages_to_chunks(page_list, document_name):
    # https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5
    min_size = 512

    chunk_list = []
    chunk_id_list = []
    chunk_meta_list = []

    page_nr = 0
    total_chunk_nr = 0

    for page_text in page_list:  # estimate about 4ms per page
        page_nr = page_nr + 1  # count pages

        chunks = [page_text]
        if len(page_text) > min_size:  # do not split pages smaller than min_size
            small_chunks = re.split(r'\.\s', page_text)  # split phrases on period + whitespace
            chunks = bigger_chunks(small_chunks, min_size)

        page_chunk_nr = 0
        for chunk in chunks:
            page_chunk_nr = page_chunk_nr + 1  # count chunks per page
            total_chunk_nr = total_chunk_nr + 1  # count total chunks

            chunk_list.append(chunk)
            chunk_id_list.append(f"{total_chunk_nr}")
            meta = {'doc': document_name,
                    'page': page_nr,
                    'chunk': page_chunk_nr,
                    'len': len(chunk),
                    'nr': total_chunk_nr}
            chunk_meta_list.append(meta)
            # optional: add summary or other meta info to chunk

    return chunk_list, chunk_id_list, chunk_meta_list
