import re

import fitz


def pdf_to_text(filename):
    page_list = []

    reader = fitz.open(filename)
    for page in reader:  # estimate about 4ms per page
        page_text = page.get_text()  # convert page from pdf to text
        page_list.append(page_text)
    return page_list


def pages_to_chunks(page_list, document_name):
    chunk_list = []
    chunk_meta_list = []
    chunk_id_list = []
    page_nr = 0
    total_chunk_nr = 0

    for page_text in page_list:  # estimate about 4ms per page
        page_nr = page_nr + 1  # count pages

        chunks = re.split(r'\.\s', page_text)  # split phrases on period + whitespace
        page_chunk_nr = 0
        for chunk in chunks:
            if len(chunk) > 5:  # no tiny chunks please TODO append tiny chunks to following chunk
                page_chunk_nr = page_chunk_nr + 1  # count chunks per page
                total_chunk_nr = total_chunk_nr + 1  # count total chunks

                chunk_list.append(chunk)
                chunk_id_list.append(f"{total_chunk_nr}")
                meta = {'doc': document_name,
                        'page': page_nr,
                        'chunk': page_chunk_nr,
                        'pos': total_chunk_nr}
                chunk_meta_list.append(meta)
                # TODO: add summary or other meta info to chunk?

    return chunk_list, chunk_id_list, chunk_meta_list
