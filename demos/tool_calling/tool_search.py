import os
import urllib.parse
from json import JSONDecodeError

import requests
from dotenv import load_dotenv

load_dotenv()

# https://developers.google.com/custom-search/v1/overview
google_api_key = os.getenv('GOOGLE_API_KEY')
google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')


def search_on_google(query: str):
    print(f"Searching on Google: '{query}'")
    query_enc = urllib.parse.quote_plus(query)
    url = f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={google_search_engine_id}&q={query_enc}'
    url += '&y=2&gl=be&safe=active'
    response = requests.get(url)

    try:
        json_response = response.json()
        return json_response
    except JSONDecodeError:
        print('WARNING: cannot decode search response')

    return response.text
