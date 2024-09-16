# JSON description of available methods
tools_weather = [{
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ]
                }
            },
            "required": [
                "location"
            ]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "get_current_rainfall",
            "description": "Get the current rainfall in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit"
                        ]
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]


# callable method for the LLM
def get_current_temperature(location, unit="Celsius"):
    print(f"get_current_temperature {location} {unit}")
    return {"temp": "20 degrees celsius"}


# callable method for the LLM
def get_current_rainfall(location, unit="mm"):
    print(f"get_current_rainfall {location} {unit}")
    return {"rainfall": "15mm"}
