import fitz

from templated.templates.document_converter import DocumentConverter


class PdfConferter(DocumentConverter):

    def convert_to_markdown_fulltext(self, file_path: str) -> str:
        page_list = self.convert_to_markdown_pages(file_path)

        full_text = ''
        for page_text in page_list:
            full_text = full_text + page_text

        return full_text

    def convert_to_markdown_pages(self, file_path: str) -> list[str]:
        page_list = []

        reader = fitz.open(file_path)
        for page in reader:  # estimate about 4ms per page
            page_text = page.get_text()  # convert page from pdf to text
            page_list.append(page_text)

        return page_list
