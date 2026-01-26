"""
Web Search Tool: Search the web using Google API.
"""
import requests
from typing import Dict, Any

from utils.config import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID


def search_on_google(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search Google for results.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        Dictionary with search results
    """
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return {
            'error': 'Google API credentials not configured',
            'results': []
        }

    try:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': query,
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'num': min(num_results, 10)
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet'),
                'kind': 'customsearch#result'
            })

        return {
            'query': query,
            'results': results,
            'total_results': data.get('queries', {}).get('request', [{}])[0].get('totalResults', 0)
        }

    except Exception as e:
        return {
            'error': f'Search failed: {str(e)}',
            'results': []
        }


# Tool descriptor for LLM
search_descriptor = {
    "type": "function",
    "function": {
        "name": "search_on_google",
        "description": "Search the web using Google Custom Search. Returns a list of relevant webpages with titles, links, and snippets. Use this to find general information, news, or specific websites.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-10)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}
