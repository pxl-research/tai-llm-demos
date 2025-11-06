import os
import sys

from dotenv import load_dotenv
from markitdown import MarkItDown

sys.path.append('../')
sys.path.append('../../')

from demos.components.open_router_client import OpenRouterClient

load_dotenv()


def document_to_markdown(doc_filename: str) -> str:
    """
    Convert a document (docx, pptx, xlsx, pdf) to Markdown text.
    """
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
