import json

import pandas as pd
import requests


def get_models(names_only=True, as_dataframe=False):
    response = requests.get('https://openrouter.ai/api/v1/models?supported_parameters=tools')  # tools only

    model_list = json.loads(response.text)
    print(f'{len(model_list['data'])} models are available.')

    # no experimental
    filtered_data = [m for m in model_list['data']
                     if 'beta' not in m['id']
                     and '-exp' not in m['id']
                     and ':free' not in m['id']]

    # context
    filtered_data = [m for m in filtered_data if m['context_length'] >= 8000]  # at least medium-size context

    # price
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['completion']) * 1000000 < 20]  # completion pricing
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['prompt']) * 1000000 < 10]  # prompt pricing

    print(f'{len(filtered_data)} models left after filtering ...\n')

    # sorting by provider, then pricing
    filtered_data.sort(key=lambda m: ((float(m['pricing']['completion']) + float(m['pricing']['prompt']) / 5),
                                      m['id'].split('/')[0]))

    if names_only and not as_dataframe:
        names = []
        for model in filtered_data:
            names.append(model['id'])
        return names

    md_data = []
    for model in filtered_data:
        ppm_p = float(model['pricing']['prompt']) * 1000000
        ppm_c = float(model['pricing']['completion']) * 1000000
        md_data.append([model['id'].split('/')[0], model['id'], ppm_p, ppm_c, model['context_length']])

    df_models = pd.DataFrame(md_data,
                             columns=['provider',
                                      'model_name',
                                      'prompt_price',
                                      'completion_price',
                                      'context_length'])
    df_models.style.background_gradient()

    pd.set_option('display.width', 200)
    pd.set_option('display.precision', 2)

    return df_models


# uncomment to see pricing in terminal
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     pp.pprint(get_models(as_dataframe=True))

# some results, taken november 5th
some_models = [
    'anthropic/claude-3-haiku',
    'anthropic/claude-3.5-sonnet',
    'anthropic/claude-3.5-sonnet-20240620',
    'anthropic/claude-3-sonnet',
    'google/gemini-flash-1.5-8b',
    'google/gemini-flash-1.5',
    'google/gemini-pro-1.5',
    'google/gemini-pro-vision',
    'meta-llama/llama-3.2-11b-vision-instruct',
    'meta-llama/llama-3.2-90b-vision-instruct',
    'openai/gpt-4o',
    'openai/gpt-4o-2024-08-06',
    'openai/gpt-4o-mini',
    'openai/gpt-4o-mini-2024-07-18',
    'openai/gpt-4o-2024-05-13'
]
