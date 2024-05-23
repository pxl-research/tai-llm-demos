import re

from class_based.superclasses.textsplitter import TextSplitter


class BasicTextSplitter(TextSplitter):
    # https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5
    min_size = 384

    def split(self, markdown_text: str, meta_info: dict = None, index_offset: int = 0) -> list:
        chunk_list = []

        chunks = [markdown_text]
        if len(markdown_text) > self.min_size:  # do not split texts smaller than min_size
            phrase_chunks = re.split(r'\.\s', markdown_text)  # split phrases on period + whitespace
            chunks = self.aggregate_chunks(phrase_chunks, self.min_size)

        chunk_nr = index_offset
        for chunk in chunks:
            chunk_nr = chunk_nr + 1  # count chunks per page

            if meta_info is None:
                meta_info = {}
            meta_info['chunk'] = chunk_nr
            meta_info['len'] = len(chunk)

            chunk_obj = {
                'text': chunk,
                'id': chunk_nr,
                'meta': meta_info
            }

            chunk_list.append(chunk_obj)

        return chunk_list

    def aggregate_chunks(self, chunk_list: list[str], min_size: int):
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
