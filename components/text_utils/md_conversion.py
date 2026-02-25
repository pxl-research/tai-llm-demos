import os
import sys

import pymupdf4llm
from dotenv import load_dotenv
from markitdown import MarkItDown

sys.path.append('../')
sys.path.append('../../demos/')

from components.open_router.open_router_client import OpenRouterClient

load_dotenv()


def document_to_markdown(doc_filename: str) -> str:
    """
    Convert a document (docx, pptx, xlsx, pdf) to Markdown text.
    """

    if doc_filename.endswith('.pdf'):
        # markitdown does not work well with pdfs so we use pymupdf4llm
        return pymupdf4llm.to_markdown(doc_filename)

    mid = MarkItDown(enable_plugins=False)
    conversion = mid.convert(doc_filename)
    return conversion.text_content


def image_description(img_filename: str) -> str:
    """
    Generate a Markdown image description using an LLM client.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    model_name = os.getenv('OPENROUTER_MODEL_NAME')

    or_client = OpenRouterClient(api_key=api_key, model_name=model_name)
    md = MarkItDown(llm_client=or_client,
                    llm_model=model_name,
                    llm_prompt='Describe the following image in detail, in Dutch, using Markdown format')
    result = md.convert(img_filename)
    return result.text_content


if __name__ == '__main__':
    # convert a document (passed as parameter) to markdown and store in a .md file
    if len(sys.argv) < 2:
        print('Usage: python md_conversion.py <document_filename>')
        sys.exit(1)

    doc_filename = sys.argv[1]
    md_text = document_to_markdown(doc_filename)
    md_filename = os.path.splitext(doc_filename)[0] + '.md'
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(md_text)
    print(f'Converted {doc_filename} to {md_filename}')
