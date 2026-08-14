import copy
import glob
import os
import random
import re
import sys

import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from thefuzz import fuzz

sys.path.append('../../')

from components.open_router.open_router_client import OpenRouterClient
from components.open_router.or_model_filtering import get_models

load_dotenv()

system_instruction = {
    'role': 'system',
    'content': 'You are a helpful assistant. '
               'Be concise, but include all relevant details. '
               'Always think step by step, '
               'but only keep a minimum draft for each thinking step, with 25 words at most. '
               'If unsure, state your assumptions. '
               'Answer using Markdown syntax to structure your text. '
               'When using an external source, always include the reference.'
}

different_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c',
                    '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#aaffc3', '#808000', '#ffd8b1', '#808080']
providers = {}

# --- LM Arena "bang for the buck" configuration --------------------------------------------
# Which lmarena_download.py --subset CSV to blend in (run that script to (re)generate it).
# One arena at a time by design; swap this to switch, rather than blending several incompatible scales.
LMARENA_SUBSET = 'text_style_control'
LMARENA_FUZZY_THRESHOLD = 75

# Reference models that calibrate the value-estimate curve (see compute_value_cost below).
# 'good' tier -> cost is left unadjusted (multiplier 1.0) at this quality level.
# 'very_good' tier -> the point where the effective cost is halved.
LMARENA_ANCHOR_GOOD = ['anthropic/claude-sonnet-4-5', 'anthropic/claude-sonnet-4-6']
LMARENA_ANCHOR_VERY_GOOD = ['anthropic/claude-opus-4-6', 'anthropic/claude-opus-4-7']

# OpenRouter provider slug -> LM Arena organization, for the handful of providers whose
# product-brand slug doesn't share a substring with LM Arena's corporate-entity name
# (e.g. OpenRouter's "qwen" vs LM Arena's "Alibaba"). Everything else is resolved by
# normalizing both names and checking for substring containment (handles cases like
# "z-ai"/"Z.ai", "mistralai"/"Mistral", "meta-llama"/"Meta", "moonshotai"/"Moonshot").
LMARENA_ORG_ALIASES = {
    'qwen': 'alibaba',
}


def normalize_org(name):
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


def canonicalize_version_numbers(name):
    """Joins short major/minor-style version numbers (e.g. '3.5', '4-6') into one indivisible
    token ('3p5', '4p6'), on both sides of the comparison. Without this, thefuzz's tokenizer
    splits '5.5' into two lone '5' tokens, which can make an unrelated model (e.g. gpt-5.5) look
    like a perfect token-subset match for a short query (e.g. gpt-3.5) purely by digit coincidence.
    Longer digit runs (date stamps like '20250929') are left alone -- they're a different token."""
    return re.sub(r'\b(\d{1,2})[.\-](\d{1,2})\b', r'\1p\2', name)


def orgs_match(provider_norm, organization):
    org_norm = normalize_org(organization)
    if LMARENA_ORG_ALIASES.get(provider_norm) == org_norm:
        return True
    return provider_norm in org_norm or org_norm in provider_norm


def load_lmarena_scores(subset):
    """Loads the most recently downloaded lmarena_<subset>_*.csv into an organization/model_name/score
    DataFrame, ready for best_fuzzy_score() to filter by organization and match by model name."""
    pattern = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'lmarena_{subset}_*.csv')
    matches = sorted(glob.glob(pattern))
    if not matches:
        print(f"Warning: no LM Arena CSV found for subset '{subset}'. "
             f"Run `python3 lmarena_download.py --subset {subset}` first.")
        return pd.DataFrame(columns=['organization', 'model_name', 'score'])

    df_scores = pd.read_csv(matches[-1], sep=';')
    df_scores = df_scores.dropna(subset=['model_name'])
    df_scores['organization'] = df_scores['organization'].fillna('')
    df_scores['model_name'] = df_scores['model_name'].str.lower().apply(canonicalize_version_numbers)
    return df_scores[['organization', 'model_name', 'score']]


def best_fuzzy_score(full_model_name, score_df, threshold=LMARENA_FUZZY_THRESHOLD):
    """Finds the best-matching LM Arena score for an OpenRouter model id, bridging OpenRouter's
    `provider/slug` ids and LM Arena's own model naming (which adds date stamps, effort suffixes
    like '-high'/'-thinking-32k', etc.).

    Matching happens in two stages: first narrow the candidate pool to the same organization
    (see orgs_match above) to rule out cross-provider false matches, then match by model name
    only -- exact, then prefix (so an exact-version match always wins over a shorter but wrong
    adjacent version number, e.g. '4-6' vs '4-7'), then fuzzy token_set_ratio as a last resort.
    token_set_ratio is used rather than token_sort_ratio/ratio because it scores a model name
    that's a full subset of a longer, suffix-decorated LM Arena entry as a near-perfect match,
    instead of penalizing it for the extra suffix tokens. Version numbers are canonicalized
    first (see canonicalize_version_numbers) so token_set_ratio's subset-leniency can't be
    fooled by two unrelated version numbers that happen to share a lone digit (e.g. 3.5 vs 5.5)."""
    provider, _, slug = full_model_name.lower().partition('/')
    slug = canonicalize_version_numbers(slug.split(':', 1)[0])  # drop ':batch' etc., 3.5/4-6 -> 3p5/4p6

    org_mask = score_df['organization'].apply(lambda org: orgs_match(normalize_org(provider), org))
    candidates = score_df[org_mask] if org_mask.any() else score_df
    names = candidates['model_name']

    exact = candidates[names == slug]
    if not exact.empty:
        return exact['score'].max()

    prefix_mask = names.apply(lambda name: name.startswith(slug)
                              and (len(name) == len(slug) or not name[len(slug)].isdigit()))
    if prefix_mask.any():
        return candidates.loc[prefix_mask, 'score'].max()

    best_score, best_ratio = None, 0
    for name, score in zip(names, candidates['score']):
        ratio = fuzz.token_set_ratio(slug, name)
        if ratio > best_ratio:
            best_score, best_ratio = score, ratio

    return best_score if best_ratio >= threshold else None


def lmarena_anchor_score(anchor_names, score_df):
    """Averages the LM Arena scores of a list of reference models (see LMARENA_ANCHOR_* above)."""
    scores = [s for s in (best_fuzzy_score(name, score_df) for name in anchor_names) if s is not None]
    return sum(scores) / len(scores) if scores else None


def compute_cost_estimate(prompt_price, completion_price):
    """Weighted API price for a rough (coding/web-dev-flavored) run: 80% prompt, 20% completion."""
    return 0.8 * prompt_price + 0.2 * completion_price


def compute_scaled_cost_estimate(lm_arena_score, cost_estimate, baseline, half_life):
    """Scales cost_estimate down for models that score above the 'good' baseline and up for
    models that score below it. A model at the 'very good' anchor tier costs half as much (in
    effective terms) as one at the baseline tier."""
    if pd.isna(lm_arena_score) or baseline is None or not half_life:
        return float('nan')

    return cost_estimate * (2 ** (-(lm_arena_score - baseline) / half_life))


# blocks UI method
def on_load_ui():
    data_models = get_models(tools_only=False,
                             image_only=False,
                             min_context=16000,
                             max_completion_price=20,
                             max_prompt_price=10,
                             skip_free=True,
                             skip_experimental=True)

    score_df = load_lmarena_scores(LMARENA_SUBSET)
    baseline = lmarena_anchor_score(LMARENA_ANCHOR_GOOD, score_df)
    very_good = lmarena_anchor_score(LMARENA_ANCHOR_VERY_GOOD, score_df)
    half_life = (very_good - baseline) if baseline is not None and very_good is not None else None

    data_models['lm_arena_score'] = data_models['full_model_name'].apply(
        lambda name: best_fuzzy_score(name, score_df))
    data_models['cost_estimate'] = compute_cost_estimate(data_models['prompt_price'], data_models['completion_price'])
    data_models['scaled_cost_estimate'] = data_models.apply(
        lambda row: compute_scaled_cost_estimate(row['lm_arena_score'], row['cost_estimate'], baseline, half_life),
        axis=1)
    data_models = data_models[['full_model_name', 'lm_arena_score', 'scaled_cost_estimate', 'prompt_price',
                               'completion_price', 'cost_estimate', 'context_length', 'max_completion_tokens',
                               'provider']]

    # set precision of price/score values
    price_columns = data_models.filter(like='price').columns
    format_dict = {col: "{:.3f}".format for col in price_columns}
    format_dict.update({col: "{:.0f}".format for col in ['max_completion_tokens']})
    format_dict.update({'lm_arena_score': "{:.0f}".format, 'cost_estimate': "{:.3f}".format,
                        'scaled_cost_estimate': "{:.3f}".format})

    style_models = (data_models.style
                    .format(format_dict, na_rep='N/A')
                    .map(colorize_quantiles, df=data_models, col='completion_price', subset=['completion_price'])
                    .map(colorize_quantiles, df=data_models, col='prompt_price', subset=['prompt_price'])
                    .map(colorize_quantiles, df=data_models, col='cost_estimate', subset=['cost_estimate'])
                    .map(colorize_quantiles, df=data_models, col='scaled_cost_estimate',
                        subset=['scaled_cost_estimate'])
                    .map(colorize_contexts, subset=['context_length'])
                    .map(colorize_providers, subset=['provider'])
                    .map(colorize_scores, df=data_models, col='lm_arena_score', subset=['lm_arena_score'])
                    )

    return data_models, style_models


# helper method
def colorize_quantiles(value, df, col):
    if value < df[col].quantile(0.3):
        return 'color:green;'
    if value >= df[col].quantile(0.9):
        return 'color:red;'
    if value > df[col].quantile(0.6):
        return 'color:orange;'
    return ''


def colorize_contexts(context_size):
    if context_size > 64000:
        return 'color:green;'
    if context_size < 10000:
        return 'color:red;'
    if context_size < 20000:
        return 'color:orange;'
    return ''


def colorize_providers(full_model_name):
    provider_name = full_model_name.split('/')[0]

    available_colors = copy.deepcopy(different_colors)
    if provider_name not in providers.keys():
        # select a random color
        color = random.choice(available_colors)
        providers[provider_name] = color
        available_colors.remove(color)

        if len(available_colors) < 1:
            # start re-using these colors when we run out
            available_colors = copy.deepcopy(different_colors)

    return 'color:' + providers[provider_name] + ';'


def colorize_scores(value, df, col):
    """Colorizes LM Arena scores based on quantiles; models with no matching score are left grey."""
    if pd.isna(value):
        return 'color:grey;'
    if value >= df[col].quantile(0.9):
        return 'color:green;'
    if value < df[col].quantile(0.35):
        return 'color:red;'
    if value < df[col].quantile(0.65):
        return 'color:orange;'
    return ''


# blocks UI method
def on_row_selected(select_data: gr.SelectData):
    # find the name of the model in the dataframe
    if select_data is not None:
        if select_data.row_value is not None:
            if len(select_data.row_value) > 0:
                return select_data.row_value[0], select_data.row_value[0]
        # fallback option 1
        print(f'Warning: using {select_data.value} as model name')
        return select_data.value, select_data.value  # value of clicked cell, might be wrong

    # fallback option 2: nothing
    return None


# blocks UI method
def append_user(user_message, chat_history, message_list):
    chat_history.append({'role': 'user', 'content': user_message})
    message_list.append({'role': 'user', 'content': user_message})
    return '', chat_history, message_list


# blocks UI method
def append_bot(chat_history, message_list, model_name):
    yield from complete_with_llm(chat_history, message_list, model_name)


# blocks UI method
def on_clear_clicked():
    # empty the chat log on screen, and the messages internally
    return [None, [system_instruction]]


def complete_with_llm(chat_history, message_list, model_name):
    or_client = OpenRouterClient(model_name=model_name,
                                 api_key=os.getenv('OPENROUTER_API_KEY'))
    response_stream = or_client.create_completions_stream(message_list=message_list)

    partial_message = ''

    chat_history.append({'role': 'assistant', 'content': ''})  # append empty response

    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0:
            # LLM text reponses
            if chunk.choices[0].delta.content is not None:
                partial_message = partial_message + chunk.choices[0].delta.content
                chat_history[-1]['content'] = partial_message
                yield chat_history, message_list

    response_stream.close()

    # handle text responses
    if chat_history[-1]['content'] is not None:
        message_list.append({'role': 'assistant', 'content': chat_history[-1]['content']})


# Gradio UI
custom_css = """
    .danger {background: red;}
    .blue {background: #247BA0;}
    footer {display:none !important}
"""
with (gr.Blocks(fill_height=True, title='OpenRouter Model Choice') as llm_client_ui):
    # state
    messages = gr.State([system_instruction])
    selected_model = gr.State('anthropic/claude-haiku-4.5')
    df_models = gr.State(None)

    # ui
    cb_live = gr.Chatbot(label='Chat',
                         scale=1,
                         buttons=["copy"])

    with gr.Group() as gr_live:
        with gr.Row():
            tb_user = gr.Textbox(show_label=False,
                                 info='Enter your prompt here.',
                                 placeholder='Enter prompt here...',
                                 scale=1)

            btn_send = gr.Button('', scale=0, min_width=64, elem_classes='blue',
                                 icon='../../assets/icons/send.png')
            btn_clear = gr.Button('', scale=0, min_width=64, elem_classes='danger',
                                  icon='../../assets/icons/disposal.png')

        lbl_model = gr.Textbox(label='Currently selected model:',
                               value=selected_model.value,
                               interactive=False,
                               elem_classes='bold')
        with gr.Row():
            with gr.Accordion(label='Available models', open=False):
                dfr_models = gr.DataFrame(df_models.value,
                                          type="pandas",
                                          show_search='search',
                                          interactive=False,
                                          headers=['Full Model Name', 'LM Arena Score', 'Scaled Cost Estimate',
                                                   'Prompt Price', 'Completion Price', 'Cost Estimate',
                                                   'Context Length', 'Max Completion Tokens', 'Provider'])

    # event handlers
    tb_user.submit(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, selected_model],
                                     [cb_live, messages])

    btn_send.click(append_user,
                   [tb_user, cb_live, messages],
                   [tb_user, cb_live, messages],
                   queue=False).then(append_bot,
                                     [cb_live, messages, selected_model],
                                     [cb_live, messages])

    btn_clear.click(on_clear_clicked,
                    None,
                    [cb_live, messages],
                    queue=False)

    llm_client_ui.load(fn=on_load_ui,
                       inputs=None,
                       outputs=[df_models, dfr_models])

    dfr_models.select(fn=on_row_selected,
                      inputs=[],
                      outputs=[lbl_model, selected_model])

llm_client_ui.queue().launch(auth=None,
                             server_name='0.0.0.0',
                             server_port=7022,
                             css=custom_css)
