import os


def cleanup_filename(full_file_path):
    cleaned_name = os.path.basename(full_file_path)  # remove path
    cleaned_name = os.path.splitext(cleaned_name)[0]  # remove extension
    cleaned_name = cleaned_name.lower()  # lowercase
    cleaned_name = cleaned_name.replace(".", "_")  # no periods
    return cleaned_name[:60]  # crop it


def repack_results(result):
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
