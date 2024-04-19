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

    for page_text in page_list:  # estimate about 4ms per page
        page_nr = page_nr + 1  # count pages

        chunks = re.split(r'\.\s', page_text)  # split phrases on period + whitespace
        chunk_nr = 0
        for chunk in chunks:
            if len(chunk) > 5:  # no tiny chunks please
                chunk_nr = chunk_nr + 1
                chunk_list.append(chunk)
                meta = {'doc': document_name,
                        'page': page_nr,
                        'chunk': chunk_nr}
                # TODO: add summary or other meta info to chunk?
                chunk_meta_list.append(meta)
                chunk_id_list.append(f"p{page_nr}_c{chunk_nr}")

    return chunk_list, chunk_id_list, chunk_meta_list
