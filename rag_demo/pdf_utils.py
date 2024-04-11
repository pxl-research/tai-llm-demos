import fitz


def pdf_to_text(filename):
    page_list = []

    reader = fitz.open(filename)
    for page in reader:  # estimate about 4ms per page
        page_text = page.get_text()  # convert page from pdf to text
        page_list.append(page_text)
    return page_list


def pages_to_chunks(page_list):
    chunk_list = []
    chunk_meta_list = []
    chunk_id_list = []
    page_nr = 0

    for page_text in page_list:  # estimate about 4ms per page
        page_nr = page_nr + 1  # count pages

        chunks = page_text.split('.')
        chunk_nr = 0
        for chunk in chunks:
            if len(chunk) > 5:  # no tiny chunks please
                chunk_nr = chunk_nr + 1
                chunk_list.append(chunk)
                meta = {'page': page_nr, 'chunk': chunk_nr}
                chunk_meta_list.append(meta)
                chunk_id_list.append(f"p{page_nr}_c{chunk_nr}")
        # TODO: add summary or other meta info?
    return chunk_list, chunk_id_list, chunk_meta_list
