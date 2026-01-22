"""
Web Scraper Tool: Extract content from webpages.
"""
import os
import requests
from typing import Dict, Any


def get_webpage_content(url: str) -> Dict[str, Any]:
    """
    Extract text content from a webpage.

    Args:
        url: URL to scrape

    Returns:
        Dictionary with page content and metadata
    """
    try:
        # Set a user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Try to use markitdown if available for better conversion
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            # Save to temp file and convert
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(response.text)
                temp_path = f.name

            result = md.convert(temp_path)
            os.unlink(temp_path)
            content = result.text_content
        except Exception:
            # Fallback: extract plain text
            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []

                def handle_data(self, data):
                    self.text.append(data.strip())

            parser = TextExtractor()
            parser.feed(response.text)
            content = ' '.join(parser.text)

        return {
            'url': url,
            'status_code': response.status_code,
            'title': response.headers.get('content-type', 'unknown'),
            'content': content[:5000],  # Limit to 5000 chars
            'content_length': len(content)
        }

    except Exception as e:
        return {
            'url': url,
            'error': f'Failed to fetch webpage: {str(e)}',
            'content': ''
        }


# Tool descriptor for LLM
scraper_descriptor = {
    "type": "function",
    "function": {
        "name": "get_webpage_content",
        "description": "Extract the text content from a webpage and return it as formatted text. This is useful for reading the full content of a specific webpage you found in a search result.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to scrape"
                }
            },
            "required": ["url"]
        }
    }
}
