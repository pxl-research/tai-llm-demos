import requests
from dotenv import load_dotenv
from markdownify import markdownify

load_dotenv()


def get_webpage_content(url: str):
    print(f"Fetching webpage: '{url}'")

    response = requests.get(url)
    markdown_text = markdownify(response.text)

    return markdown_text
