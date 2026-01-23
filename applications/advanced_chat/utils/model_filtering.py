"""
Model filtering utilities - copied from components/open_router/or_model_filtering.py
Self-contained for this application.
"""
import json
import pandas as pd
import requests

PRICE_FACTOR = 1000000


def get_models(tools_only=False,
               image_only=False,
               min_context=0,
               max_completion_price=0,
               max_prompt_price=0,
               skip_free=True,
               skip_experimental=True,
               exacto_only=False):
    """
    Fetch and filter models from OpenRouter API.

    Args:
        tools_only: Only return models that support tool calling
        image_only: Only return models that support image inputs
        min_context: Minimum context length
        max_completion_price: Maximum completion price per million tokens
        max_prompt_price: Maximum prompt price per million tokens
        skip_free: Skip free models (typically rate-limited)
        skip_experimental: Skip beta/experimental models
        exacto_only: Only return exacto models

    Returns:
        DataFrame with filtered models
    """
    models_url = 'https://openrouter.ai/api/v1/models'
    if tools_only:
        models_url += '?supported_parameters=tools'

    response = requests.get(models_url)
    model_list = json.loads(response.text)
    print(f'{len(model_list["data"])} models are available.')

    filtered_data = model_list['data']

    if skip_experimental:
        filtered_data = [m for m in filtered_data if
                         not any(term in m['id'] for term in ['beta', '-exp', ':free'])]

    # context
    if min_context > 0:
        filtered_data = [m for m in filtered_data if m['context_length'] >= min_context]

    # price
    if max_completion_price > 0:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['completion']) * PRICE_FACTOR <= max_completion_price]

    if max_prompt_price > 0:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['prompt']) * PRICE_FACTOR <= max_prompt_price]

    if skip_free:
        filtered_data = [m for m in filtered_data if
                         float(m['pricing']['prompt']) > 0]

    # modality
    if image_only:
        filtered_data = [m for m in filtered_data if
                         'image' in m.get('architecture', {}).get('input_modalities', [])
                         and 'text' in m.get('architecture', {}).get('input_modalities', [])]

    if exacto_only:
        filtered_data = [m for m in filtered_data if ':exacto' in m['id']]

    print(f'{len(filtered_data)} models left after filtering ...\n')

    md_data = []
    for model in filtered_data:
        ppm_p = float(model['pricing']['prompt']) * PRICE_FACTOR
        ppm_c = float(model['pricing']['completion']) * PRICE_FACTOR
        md_data.append([model['id'],
                        ppm_p,
                        ppm_c,
                        model['context_length'],
                        model['top_provider']['max_completion_tokens'],
                        model['id'].split('/')[0]])

    df_models = pd.DataFrame(md_data,
                             columns=['full_model_name',
                                      'prompt_price',
                                      'completion_price',
                                      'context_length',
                                      'max_completion_tokens',
                                      'provider'])
    df_models = df_models.drop_duplicates()

    # sorting - order by provider, then by capabilities (descending), then by name
    df_models.sort_values(
        by=[
            'provider',              # Group by provider (A-Z)
            'completion_price',      # Expensive first (high to low)
            'prompt_price',          # Expensive first (high to low)
            'context_length',        # Large context first (high to low)
            'max_completion_tokens', # Large completion first (high to low)
            'full_model_name'        # Alphabetical within same specs (A-Z)
        ],
        ascending=[True, False, False, False, False, True],
        inplace=True
    )

    # styling
    df_models.style.background_gradient()
    pd.set_option('display.width', 200)
    pd.set_option('display.precision', 3)

    return df_models
