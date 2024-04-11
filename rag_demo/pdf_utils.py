import fitz


def pdf_to_text(filename):
    page_list = []

    reader = fitz.open(filename)
    for page in reader:  # estimate about 4ms per page
        page_text = page.get_text()  # convert page from pdf to text
        page_list.append(page_text)
    return page_list


# example code
# filename = "documents/ArbeidsreglementV8.pdf"
# page_list = pdf_to_text(filename)
# print(f"Converted {len(page_list)} pages from '{filename}'")
