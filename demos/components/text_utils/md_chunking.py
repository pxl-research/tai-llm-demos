import re


def split_by_header(md_text: str, header_level: int = 1) -> list[str]:
    """
    Splits Markdown text into sections based on the specified header level.
    For example, header_level=1 splits on '# ', header_level=2 splits on '## ', etc.
    """
    header_pattern = r'(?=^' + r'#' * header_level + r' )'
    sections = re.split(header_pattern, md_text, flags=re.MULTILINE)
    return [sec for sec in sections if sec.strip()]  # Remove empty sections


def split_by_newlines(text: str, newline_count: int = 2) -> list[str]:
    """
    Splits text into sections based on consecutive newlines.
    newline_count=2 splits on two or more newlines (with optional whitespace).
    """
    # Pattern: match at least `newline_count` newlines, allowing optional whitespace
    pattern = r'\n{' + str(newline_count) + r',}\s*'
    sections = re.split(pattern, text)
    return [sec.strip() for sec in sections if sec.strip()]


def split_on_sentences(text: str) -> list[str]:
    """
    Splits text into sentences, including the trailing punctuation (.?!) and preserving it in the chunk.
    Uses: period, question mark, or exclamation followed by one or more whitespace.
    """
    # Pattern: positive lookbehind to keep punctuation, split on whitespace after
    pattern = r'(?<=[.!?])\s+'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def split_on_threshold(text: str, max_chars: int = 1024, overlap_pct: float = 0.05) -> list[str]:
    """
    Splits text into chunks of max_chars, rounding back to the previous whitespace to avoid mid-word breaks.
    Optional overlap (as integer chars) can be added between chunks.
    """
    chunks = []
    start = 0
    txt_len = len(text)
    overlap = int(max_chars * overlap_pct)

    while start < txt_len:
        end = min(start + max_chars, txt_len)
        if end == txt_len:
            chunk = text[start:end]
            chunks.append(chunk)
            break

        # Find last whitespace before max_chars to avoid breaking words
        last_whitespace = text.rfind(' ', start, end)
        if last_whitespace == -1:  # No whitespace found, force break at end
            chunk_end = end
        else:
            chunk_end = last_whitespace

        chunk = text[start:chunk_end].strip()
        if chunk:
            chunks.append(chunk)

        # Set next start, with optional overlap
        if overlap > 0 and chunk_end - overlap >= 0:
            start = chunk_end - overlap
            # find whitespace to avoid mid-word start
            last_whitespace = text.rfind(' ', 0, start)
            if last_whitespace != -1:
                start = last_whitespace
        else:
            start = chunk_end

        # TODO: prevent infinite loop if no progress

    return chunks


def iterative_chunking(md_text: str, max_size: int = 1024) -> list[str]:
    """
    Iteratively chunk Markdown text using multiple strategies until all chunks are under max_size.
    Strategies: header levels, newlines, sentences, threshold.
    """
    chunks = [md_text]

    # list of chunking strategies, from coarse to fine
    strategies = [
        lambda text: split_by_header(text, header_level=1),
        lambda text: split_by_header(text, header_level=2),
        lambda text: split_by_header(text, header_level=3),
        lambda text: split_by_header(text, header_level=4),
        lambda text: split_by_header(text, header_level=5),
        lambda text: split_by_header(text, header_level=6),
        lambda text: split_by_newlines(text, newline_count=4),
        lambda text: split_by_newlines(text, newline_count=3),
        lambda text: split_by_newlines(text, newline_count=2),
        lambda text: split_by_newlines(text, newline_count=1),
        split_on_sentences,
        lambda text: split_on_threshold(text, max_chars=max_size, overlap_pct=0.1)
    ]
    strat = 0

    while True:
        # if all chunks are small enough, return
        if all(len(chunk) <= max_size for chunk in chunks):
            return chunks

        for c in range(len(chunks)):
            big_chunk = chunks[c]
            if len(big_chunk) <= max_size:
                continue

            # apply current strategy to big chunk
            new_chunks = strategies[strat](big_chunk)
            if len(new_chunks) > 1:
                # merge small chunks if needed
                new_chunks = merge_small_chunks(new_chunks, max_size=max_size)

            # replace original big chunk with new chunks
            chunks = chunks[:c] + new_chunks + chunks[c + 1:]

        # try next strategy if available
        if strat < len(strategies) - 1:
            strat += 1


def merge_small_chunks(small_chunks: list[str], max_size: int = 1024) -> list[str]:
    """
    Merge consecutive chunks if their combined size is <= max_size.
    Returns a list of merged chunks optimized for size.
    """
    merged = []
    current = ''

    for chunk in small_chunks:
        # if adding chunk keeps size under max_size, merge
        if len(current) + len(chunk) <= max_size:
            current = (current + chunk).strip()
        else:
            if current:
                merged.append(current)
            current = chunk
    if current:
        merged.append(current)

    return merged
