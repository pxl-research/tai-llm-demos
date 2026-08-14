import glob
import os
import re

import pandas as pd
from thefuzz import fuzz

# Which lmarena_download.py --subset CSV to blend in by default (run that script to (re)generate it).
# One arena at a time by design; swap this to switch, rather than blending several incompatible scales.
LMARENA_SUBSET = 'text_style_control'
LMARENA_FUZZY_THRESHOLD = 75

# Reference models that calibrate the scaled-cost-estimate curve (see compute_scaled_cost_estimate below).
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


def normalize_lmarena_df(df_scores):
    """Cleans a raw LM Arena leaderboard DataFrame (as returned by lmarena_download.download_leaderboard,
    or read straight from one of its CSVs) into the organization/model_name/score shape that
    best_fuzzy_score() expects."""
    df_scores = df_scores.dropna(subset=['model_name']).copy()
    df_scores['organization'] = df_scores['organization'].fillna('')
    df_scores['model_name'] = df_scores['model_name'].str.lower().apply(canonicalize_version_numbers)
    return df_scores[['organization', 'model_name', 'score']]


def load_lmarena_scores(subset):
    """Loads the most recently downloaded lmarena_<subset>_*.csv into an organization/model_name/score
    DataFrame, ready for best_fuzzy_score() to filter by organization and match by model name."""
    pattern = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'lmarena_{subset}_*.csv')
    matches = sorted(glob.glob(pattern))
    if not matches:
        print(f"Warning: no LM Arena CSV found for subset '{subset}'. "
             f"Run `python3 lmarena_download.py --subset {subset}` first.")
        return pd.DataFrame(columns=['organization', 'model_name', 'score'])

    return normalize_lmarena_df(pd.read_csv(matches[-1], sep=';'))


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
    return round(0.8 * prompt_price + 0.2 * completion_price, 2)


def compute_scaled_cost_estimate(lm_arena_score, cost_estimate, baseline, half_life):
    """Scales cost_estimate down for models that score above the 'good' baseline and up for
    models that score below it. A model at the 'very good' anchor tier costs half as much (in
    effective terms) as one at the baseline tier."""
    if pd.isna(lm_arena_score) or baseline is None or not half_life:
        return float('nan')

    return round(cost_estimate * (2 ** (-(lm_arena_score - baseline) / half_life)), 2)


def enrich_with_lmarena(data_models, score_df):
    """Adds lm_arena_score, cost_estimate and scaled_cost_estimate columns to an OpenRouter
    pricing DataFrame (as returned by or_model_filtering.get_models), and reorders the columns
    for display. score_df should come from load_lmarena_scores() or normalize_lmarena_df()."""
    baseline = lmarena_anchor_score(LMARENA_ANCHOR_GOOD, score_df)
    very_good = lmarena_anchor_score(LMARENA_ANCHOR_VERY_GOOD, score_df)
    half_life = (very_good - baseline) if baseline is not None and very_good is not None else None

    data_models = data_models.copy()
    data_models['lm_arena_score'] = data_models['full_model_name'].apply(
        lambda name: best_fuzzy_score(name, score_df))
    data_models['cost_estimate'] = compute_cost_estimate(data_models['prompt_price'], data_models['completion_price'])
    data_models['scaled_cost_estimate'] = data_models.apply(
        lambda row: compute_scaled_cost_estimate(row['lm_arena_score'], row['cost_estimate'], baseline, half_life),
        axis=1)

    data_models = data_models[['full_model_name', 'lm_arena_score', 'prompt_price', 'completion_price',
                               'cost_estimate', 'scaled_cost_estimate', 'context_length', 'max_completion_tokens',
                               'provider']]
    return data_models.round(2)  # belt-and-suspenders: no long floating-point tails in any numeric column
