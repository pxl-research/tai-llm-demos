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
