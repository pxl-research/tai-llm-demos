import os
import re


#  Expects a collection name that
#  (1) contains 3-63 characters,
#  (2) starts and ends with an alphanumeric character,
#  (3) otherwise contains only alphanumeric characters, underscores or hyphens (-),
#  (4) contains no two consecutive periods (..) and
#  (5) is not a valid IPv4 address

def sanitize_filename(full_file_path):
    cleaner_name = os.path.basename(full_file_path)  # remove path
    cleaner_name = os.path.splitext(cleaner_name)[0]  # remove extension
    cleaner_name = sanitize_string(cleaner_name)
    return cleaner_name[:60]  # crop it


def sanitize_string(some_text):
    cleaner_name = some_text.strip()
    cleaner_name = cleaner_name.replace(" ", "_")  # spaces to underscores
    cleaner_name = re.sub(r'[^a-zA-Z0-9_-]', '-', cleaner_name)  # replace invalid characters with spaces
    cleaner_name = cleaner_name.rstrip('-')  # remove trailing dashes
    return cleaner_name


def repack_query_results(result):
    fields = ['distances', 'metadatas', 'embeddings', 'documents', 'uris', 'data']
    length = len(result['ids'][0])  # ids are always returned
    repacked = []
    for r in range(length):
        repacked_result = {'ids': result['ids'][0][r]}
        for field in fields:
            if result[field] is not None:
                repacked_result[field] = result[field][0][r]
        repacked.append(repacked_result)
    return repacked


def doc_to_chunks(doc_contents, document_name):
    # https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5
    max_size = 2048

    chunk_list = []
    chunk_id_list = []
    chunk_meta_list = []
    section_nr = 0
    total_chunk_nr = 0

    section_list = re.split(r'^(#{1,6})\s+(.+)$', doc_contents)  # split on markdown headers

    for section in section_list:
        section_nr = section_nr + 1  # count sections

        chunks = split_in_chunks(section, max_size)
        section_chunk_nr = 0
        for chunk in chunks:
            section_chunk_nr = section_chunk_nr + 1  # count chunks per page
            total_chunk_nr = total_chunk_nr + 1  # count total chunks

            chunk_list.append(chunk)
            chunk_id_list.append(f"{total_chunk_nr}")
            meta = {
                'doc': document_name,
                'section': section_nr,
                'chunk': section_chunk_nr,
                'len': len(chunk),
                'nr': total_chunk_nr
            }
            chunk_meta_list.append(meta)

    return chunk_list, chunk_id_list, chunk_meta_list


def split_by_max_length(large_chunk, max_size):
    chunk_list = []
    remainder = large_chunk
    while len(remainder) > max_size:
        last_space = remainder.rfind(' ', 0, max_size)
        chunk_list.append(remainder[:last_space])
        remainder = remainder[last_space:]
    chunk_list.append(remainder)  # last part

    return chunk_list


def split_in_chunks(section_text, max_size):
    phrase_chunks = re.split(r'\.\s', section_text)  # split into "phrases" with period + whitespace

    small_chunks = []
    for phrase in phrase_chunks:
        if len(phrase) >= max_size:  # chunk is too big, make smaller
            small_chunks.extend(split_by_max_length(phrase, max_size))
        else:
            small_chunks.append(phrase)

    chunk_list = []
    current_chunk = ''
    for chunk in small_chunks:
        chunk = chunk.strip()
        if len(current_chunk) + len(chunk) >= max_size:
            chunk_list.append(current_chunk)  # add to list
            current_chunk = chunk  # start with next chunk
        else:
            current_chunk = f"{current_chunk}.\n{chunk}"  # stick together

    chunk_list.append(current_chunk)  # append last chunk

    return chunk_list
