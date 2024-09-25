# JSON description of available methods

# RAG
tools_rag_descriptor = {
    "type": "function",
    "function": {
        "name": "lookup_in_documentation",
        "description": "Get snippets from documents related to the domain you operate in."
                       "Use this as a search engine and put in natural language questions or statements as search queries. "
                       "The method will return an array of JSON objects, containing a 'documents' part with the associated text, "
                       "a 'distances' value indicating how well the info matches your question (smaller numbers are better), "
                       "and a 'metadatas' object with some info about the text chunks: document name, page number, and a paragraph (chunk) number. "
                       "Always include the document name and page number when referencing this documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "A natural language question about company rules or policies"}
            },
            "required": ["query"],
        },
    }
}

# "weather" demo
tools_weather_descriptor = [{
    'type': 'function',
    'function': {
        'name': 'get_current_temperature',
        'description': 'Get the current temperature in a given location',
        'parameters': {
            'type': 'object',
            'properties': {
                'location': {
                    'type': 'string',
                    'description': 'The city and state, e.g. San Francisco, CA'
                },
                'unit': {
                    'type': 'string',
                    'enum': [
                        'celsius',
                        'fahrenheit'
                    ]
                }
            },
            'required': [
                'location'
            ]
        }
    }
},
    {
        'type': 'function',
        'function': {
            'name': 'get_current_rainfall',
            'description': 'Get the current rainfall in a given location',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The city and state, e.g. San Francisco, CA'
                    },
                    'unit': {
                        'type': 'string',
                        'enum': [
                            'celsius',
                            'fahrenheit'
                        ]
                    }
                },
                'required': [
                    'location'
                ]
            }
        }
    }
]

tools_search_descriptor = {
    "type": "function",
    "function": {
        "name": "search_on_google",
        "description": "Use this as a classic web search engine that will provide you with a list of webpages. "
                       "The method will return a selection of nested JSON objects with information about the search and its answers. "
                       "The results will usually be labeled with 'kind': 'customsearch#result', "
                       "and contain a snippet that shows a brief summary on what to expect on a specific site. "
                       "If you need more details from a webpage, use another tool (if available) to retrieve the full page."
                       "Always include the website 'url' when referencing a search result.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "a query for Google, searching for relevant websites"}
            },
            "required": ["query"],
        },
    }
}

tools_get_website_contents = [
    {
        "type": "function",
        "function": {
            "name": "get_webpage_content",
            "description": "This method will download the HTML contents of a page and return them as Markdown. "
                           "You can use this to get more details on a page you found in a document or through a web search. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string",
                            "description": "a valid address (url) for an existing online website"}
                },
                "required": ["url"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_webpage_with_js",
            "description": "This method will download the HTML contents of a page with JavaScript and return them as Markdown. "
                           "You can use this to get more details on a page you found in a document or through a web search. "
                           "This method may be somewhat slower, but more appropriate for complex (JS rich) pages. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string",
                            "description": "a valid address (url) for an existing online website"}
                },
                "required": ["url"],
            },
        }
    }
]
