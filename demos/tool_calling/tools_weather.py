# callable method for the LLM
def get_current_temperature(location, unit='Celsius'):
    print(f'get_current_temperature {location} {unit}')
    return {'temp': '20 degrees celsius'}


# callable method for the LLM
def get_current_rainfall(location, unit='mm'):
    print(f'get_current_rainfall {location} {unit}')
    return {'rainfall': '15mm'}
