import json
import pprint as pp

import pandas as pd
import requests


def get_models(tools_only=True, names_only=True, as_dataframe=False):
    models_url = 'https://openrouter.ai/api/v1/models'
    if tools_only:
        models_url += '?supported_parameters=tools'

    response = requests.get(models_url)

    model_list = json.loads(response.text)
    print(f'{len(model_list['data'])} models are available.')

    # no experimental
    filtered_data = [m for m in model_list['data']
                     if 'beta' not in m['id']
                     and '-exp' not in m['id']
                     and ':free' not in m['id']]

    # context
    filtered_data = [m for m in filtered_data if m['context_length'] >= 16000]  # at least medium-size context

    # price
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['completion']) * 1000000 < 20]  # completion pricing
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['prompt']) * 1000000 < 10]  # prompt pricing
    filtered_data = [m for m in filtered_data if
                     float(m['pricing']['prompt']) > 0]  # remove free ones because they are rate limited

    print(f'{len(filtered_data)} models left after filtering ...\n')

    # sorting by provider, then pricing
    filtered_data.sort(
        key=lambda m: (m['id'].split('/')[0], float(m['pricing']['prompt']), float(m['pricing']['completion'])))

    if names_only and not as_dataframe:
        names = []
        for model in filtered_data:
            names.append(model['id'])
        return no_duplicates(names)

    md_data = []
    for model in filtered_data:
        ppm_p = float(model['pricing']['prompt']) * 1000000
        ppm_c = float(model['pricing']['completion']) * 1000000
        md_data.append([model['id'].split('/')[0],
                        model['id'],
                        ppm_p,
                        ppm_c,
                        model['context_length'],
                        model['top_provider']['max_completion_tokens']])

    df_models = pd.DataFrame(md_data,
                             columns=['provider',
                                      'model_name',
                                      'prompt_price',
                                      'completion_price',
                                      'context_length',
                                      'max_completion_tokens'])
    df_models = df_models.drop_duplicates()
    df_models.style.background_gradient()

    pd.set_option('display.width', 200)
    pd.set_option('display.precision', 2)

    df_models.to_csv('or_pricing.csv')

    return df_models


def no_duplicates(list_with_duplicates):
    return list(dict.fromkeys(list_with_duplicates))


# uncomment to see pricing in terminal
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     pp.pprint(get_models(tools_only=False, as_dataframe=True))

# some results, taken november 5th
some_models = [
    'ai21/jamba-1-5-mini',
    'ai21/jamba-1-5-large',
    'anthropic/claude-3-haiku',
    'anthropic/claude-3.5-haiku',
    'anthropic/claude-3.5-haiku-20241022',
    'anthropic/claude-3.5-sonnet',
    'anthropic/claude-3.5-sonnet-20240620',
    'anthropic/claude-3-sonnet',
    'cohere/command-r-08-2024',
    'cohere/command-r-03-2024',
    'cohere/command-r',
    'cohere/command-r-plus-08-2024',
    'cohere/command-r-plus',
    'cohere/command-r-plus-04-2024',
    'deepseek/deepseek-chat',
    'google/gemini-flash-1.5-8b',
    'google/gemini-flash-1.5',
    'google/gemini-pro',
    'google/gemini-pro-1.5',
    'meta-llama/llama-3.2-1b-instruct',
    'meta-llama/llama-3.2-3b-instruct',
    'meta-llama/llama-3.1-8b-instruct',
    'meta-llama/llama-3-8b-instruct',
    'meta-llama/llama-3.2-11b-vision-instruct',
    'meta-llama/llama-3.1-70b-instruct',
    'meta-llama/llama-3-70b-instruct',
    'meta-llama/llama-3.2-90b-vision-instruct',
    'meta-llama/llama-3.1-405b-instruct',
    'microsoft/phi-3-mini-128k-instruct',
    'microsoft/phi-3.5-mini-128k-instruct',
    'microsoft/phi-3-medium-128k-instruct',
    'mistralai/ministral-3b',
    'mistralai/mistral-7b-instruct',
    'mistralai/mistral-7b-instruct-v0.3',
    'mistralai/ministral-8b',
    'mistralai/mistral-nemo',
    'mistralai/mixtral-8x7b-instruct',
    'mistralai/mistral-tiny',
    'mistralai/codestral-mamba',
    'mistralai/mistral-small',
    'mistralai/mixtral-8x22b-instruct',
    'mistralai/mistral-large',
    'mistralai/mistral-large-2407',
    'mistralai/mistral-large-2411',
    'mistralai/pixtral-large-2411',
    'mistralai/mistral-medium',
    'nvidia/llama-3.1-nemotron-70b-instruct',
    'openai/gpt-4o-mini',
    'openai/gpt-4o-mini-2024-07-18',
    'openai/gpt-3.5-turbo',
    'openai/gpt-3.5-turbo-0125',
    'openai/gpt-3.5-turbo-1106',
    'openai/gpt-3.5-turbo-16k',
    'openai/gpt-4o',
    'openai/gpt-4o-2024-08-06',
    'openai/gpt-4o-2024-11-20',
    'openai/gpt-4o-2024-05-13',
    'qwen/qwen-2.5-72b-instruct'
]
