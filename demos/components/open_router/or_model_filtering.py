import json
import pprint as pp

import pandas as pd
import requests

PRICE_FACTOR = 1000000


def get_models(tools_only=False,
               image_only=False,
               min_context=0,  # good value: 16000
               max_completion_price=0,  # good value: 20
               max_prompt_price=0,  # good value: 10
               skip_free=True,
               skip_experimental=True):
    models_url = 'https://openrouter.ai/api/v1/models'
    if tools_only:
        models_url += '?supported_parameters=tools'

    response = requests.get(models_url)
    model_list = json.loads(response.text)
    print(f'{len(model_list['data'])} models are available.')

    filtered_data = model_list['data']

    if skip_experimental:
        filtered_data = [m for m in filtered_data if
                         not any(term in m['id'] for term in ['beta', '-exp', ':free'])]  # remove experimental / beta

    # context
    if min_context > 0:
        filtered_data = [m for m in filtered_data if m['context_length'] >= min_context]  # at least medium-size context

    # price
    if max_completion_price > 0:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['completion']) * PRICE_FACTOR <= max_completion_price]  # completion pricing

    if max_prompt_price > 0:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['prompt']) * PRICE_FACTOR <= max_prompt_price]  # prompt pricing

    if skip_free:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['prompt']) > 0]  # remove free ones because they are rate limited

    if image_only:
        filtered_data = [m for m in filtered_data if
                         'image' in m.get('architecture', {}).get('input_modalities', [])
                         and 'text' in m.get('architecture', {}).get('input_modalities', [])]  # image input support

    print(f'{len(filtered_data)} models left after filtering ...\n')

    md_data = []
    for model in filtered_data:
        ppm_p = float(model['pricing']['prompt']) * PRICE_FACTOR
        ppm_c = float(model['pricing']['completion']) * PRICE_FACTOR
        md_data.append([model['id'],  # full_model_name
                        ppm_p,  # prompt_price
                        ppm_c,  # completion_price
                        model['context_length'],  # context_length
                        model['top_provider']['max_completion_tokens'],  # max_completion_tokens
                        model['id'].split('/')[0]])  # provider

    df_models = pd.DataFrame(md_data,
                             columns=['full_model_name',
                                      'prompt_price',
                                      'completion_price',
                                      'context_length',
                                      'max_completion_tokens',
                                      'provider'])
    df_models = df_models.drop_duplicates()

    # sorting
    df_models['token_sum'] = df_models['max_completion_tokens'] + df_models['context_length']
    df_models.sort_values(by=['provider', 'token_sum', 'completion_price', 'prompt_price', 'full_model_name'],
                          ascending=[True, False, False, False, False],
                          inplace=True)
    df_models = df_models.drop(columns=['token_sum'])

    # styling
    df_models.style.background_gradient()
    pd.set_option('display.width', 200)
    pd.set_option('display.precision', 3)

    # saving
    df_models.to_csv('or_models.csv')

    return df_models


def no_duplicates(list_with_duplicates):
    return list(dict.fromkeys(list_with_duplicates))


# some quick tests
if __name__ == "__main__":
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        models = get_models(tools_only=True,
                            image_only=False,
                            min_context=64000,
                            max_completion_price=100,
                            max_prompt_price=20,
                            skip_free=True,
                            skip_experimental=True)
        pp.pprint(models)
