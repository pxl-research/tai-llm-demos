import glob
import os
import re

import pandas as pd

# A prefix/token match whose OpenRouter price differs from arena.ai's own displayed price for
# the matched candidate by more than this factor (either the input or the output leg) is
# rejected outright -- see best_match_score. Exact-name matches are exempt: two independently
# hosted copies of the literal same model id can genuinely differ in price (different
# provider, markup), so identical naming is trusted on its own without a price check.
PRICE_MISMATCH_TOLERANCE = 2.0

# Percentiles of a report's own matched scores that calibrate scaled_cost_estimate's linear
# interpolation (see _cost_anchors/compute_scaled_cost_estimate below) -- self-calibrating so
# "low"/"high" are always relative to what's actually on the board right now. A pair of fixed
# named-model anchors was tried first and abandoned: whichever specific models get picked
# inevitably drift relative to both each other and the current frontier as the leaderboard moves
# on, which silently broke the curve (confirmed live: two "good"-tier reference models ended up
# only ~17 points apart while the actual top of the board sat ~155 points above them, discounting
# top models ~500x instead of the intended ~2x). Mirrors html_report._score_anchors()'s use of
# the same percentiles for color.
COST_SCALE_LOW_PERCENTILE = 0.1
COST_SCALE_HIGH_PERCENTILE = 0.9

# At COST_SCALE_LOW_PERCENTILE, cost_estimate is penalized by this factor; at
# COST_SCALE_HIGH_PERCENTILE, discounted by 1/this factor (symmetric by construction). Linearly
# interpolated in between, and extrapolated at the same slope beyond either bound rather than
# clamped there -- checked live that real outliers sit close enough to the two percentiles that
# this stays gentle (worst case ~1.4x on a real report). A hard clamp was considered and
# rejected: an earlier exponential version of this curve was already steep enough that nearly
# the whole top/bottom decile blew past any reasonable cap, so clamping would just flatten most
# of the interesting range to one identical multiplier instead of the smooth spread this
# (unclamped, linear) version gives everything between the two percentiles.
COST_SCALE_MAX_FACTOR = 1.25

# OpenRouter provider slug -> LM Arena organization, for the handful of providers whose
# product-brand slug doesn't share a substring with LM Arena's corporate-entity name
# (e.g. OpenRouter's "qwen" vs LM Arena's "Alibaba"). Everything else is resolved by
# normalizing both names and checking for substring containment (handles cases like
# "z-ai"/"Z.ai", "mistralai"/"Mistral", "meta-llama"/"Meta", "moonshotai"/"Moonshot").
LMARENA_ORG_ALIASES = {
    'qwen': 'alibaba',
}

# Tokens that must never appear only on the candidate side of a match -- i.e. the query didn't
# ask for them, but the candidate has them anyway. These mark a genuinely different, usually
# separately-priced product SKU rather than an alternate mode of the same model, so a match
# that would only work by silently picking one up is rejected rather than guessed at. This is
# deliberately a short, curated list, not a general decoration-tolerance switch: reasoning-effort
# / "mode" words like "thinking" are NOT here, since LM Arena's own data shows they rarely carry
# a materially different price -- landing on an unrequested "thinking" variant is an acceptable
# imprecision, but landing on an unrequested "turbo" (almost always a separate, faster/pricier
# tier) is not. The size/tier words were added in Nov 2026 after a dry run over every LM Arena
# subset: they removed 6 wrong matches (e.g. 'sonar' -> 'sonar pro', 'o3' -> 'o3-mini') and no
# correct ones -- a query that asks for the word itself ('gemini-2.5-flash') is unaffected.
DENIED_UNREQUESTED_TOKENS = {'turbo', 'mini', 'nano', 'small', 'lite', 'flash', 'air', 'pro', 'plus', 'ultra', 'next'}

# OpenRouter ids that are rolling aliases for "the current version" without saying so (unlike
# '-latest', see _best_match): which pinned model they point at isn't knowable from the id, and
# matching by name lands on an unrelated old entry (deepseek-chat -> 2023's 'DeepSeek LLM 67B
# Chat', mistral-large -> whichever 'Mistral Large N' is listed). Refused outright, like '-latest'.
UNPINNED_ALIASES = {'deepseek/deepseek-chat', 'mistralai/mistral-large'}

# Provider (normalized, same key space as LMARENA_ORG_ALIASES) -> the trailing effort-level
# words verified NOT to double as a brand/tier name for that vendor, so an arena entry that
# differs from an OpenRouter row only by one of these words is the same priced product, just
# at a different effort setting -- unlike DENIED_UNREQUESTED_TOKENS, deliberately NOT
# vendor-agnostic (e.g. 'medium' is Mistral's own tier name, not an effort dial, so Mistral is
# not here). Starts narrow, from words actually observed on real leaderboard data; extend
# case-by-case as new ones are verified, not by guessing. See _effort_siblings.
# Keyed by the normalized OpenRouter provider slug (e.g. 'x-ai' -> 'xai'). Last verified
# against all LM Arena subsets + OpenRouter in Nov 2026: each word only ever appears inside an
# arena effort parenthetical for that vendor. Known near-miss: OpenRouter's separate
# 'openai/gpt-5.1-codex-max' product -- safe as long as no arena entry is named "... Codex Max"
# outside parentheses (that row itself can't gain false siblings: its own 'max' is required).
# alibaba deliberately has no 'max': Qwen...-Max is a product tier.
EFFORT_SIBLING_WORDS = {
    'anthropic': {'medium', 'high', 'xhigh', 'max'},
    'openai': {'low', 'medium', 'high', 'xhigh', 'max'},
    'google': {'minimal', 'medium', 'high'},
    'zai': {'max'},
    'deepseek': {'high', 'max'},
    'meta': {'xhigh', 'max'},
    'moonshotai': {'max'},
    'xai': {'high', 'xhigh'},
}

# 6-8 digit release-date stamps (e.g. 20250929, 250929) carried by either side's name -- dropped
# during tokenization so a query and candidate that differ only by a pinned date can still match.
_DATE_TOKEN = re.compile(r'^\d{6,8}$')


def normalize_org(name):
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


def canonicalize_version_numbers(name):
    """Joins short major/minor-style version numbers (e.g. '3.5', '4-6') into one indivisible
    token ('3p5', '4p6'), on both sides of the comparison. Without this, a plain word-split
    tokenizer splits '5.5' into two lone '5' tokens, which can make an unrelated model (e.g.
    gpt-5.5) look like a token-for-token match for a short query (e.g. gpt-3.5) purely by digit
    coincidence. Longer digit runs (date stamps like '20250929') are left alone -- they're a
    different token, dropped separately by tokenization (see _tokenize).

    The version number doesn't need a separator before it: Qwen glues its version straight onto
    the brand name ('qwen3.8-max', no space or dash before '3'), so the leading boundary only
    requires the previous character not be a digit or dot -- letters count as a valid start."""
    return re.sub(r'(?<![\d.])(\d{1,2})[.\-](\d{1,2})\b', r'\1p\2', name)


def _tokenize(name):
    """Splits a canonicalized name into its word/number tokens as a set, dropping trailing
    release-date stamps and 'preview' -- a temporal/beta status marker in practice (OpenAI,
    Google), not a distinguishing product tier, unlike the words in DENIED_UNREQUESTED_TOKENS."""
    return frozenset(t for t in re.findall(r'[a-z0-9]+', name) if t != 'preview' and not _DATE_TOKEN.match(t))


def _prefix_boundary_safe(name, prefix_len):
    """A prefix match is only safe if it ends on a token boundary: the next character must not
    be a letter or digit, so the candidate can't just continue the query's last token. That
    rejects a longer version number ('claude-opus-4-6' vs '4-67'), a canonicalized decimal
    ('mistral-medium-3' vs '3.5', i.e. '...-3' vs '...-3p5') and a glued-on letter ('gpt-4' vs
    'gpt-4o', a different model)."""
    return prefix_len == len(name) or not name[prefix_len].isalnum()


def _has_unrequested_denied_token(slug_tokens, candidate_name):
    return bool((_tokenize(candidate_name) - slug_tokens) & DENIED_UNREQUESTED_TOKENS)


def _closest_unique_candidate(matches):
    """matches is a list of (name, score, extra_token_count). Returns the (name, score) with
    the fewest extra tokens beyond the query -- unless more than one candidate ties for
    fewest, in which case which one the query means is genuinely ambiguous (e.g. a bare
    'gpt-5' against both 'gpt-5-high' and 'gpt-5-medium', one extra token each) and None is
    returned rather than picking one by arena score, which would just be a different-looking
    version of the same silent-guess problem this whole matcher exists to avoid."""
    if not matches:
        return None
    matches = sorted(matches, key=lambda m: m[2])
    if len(matches) > 1 and matches[0][2] == matches[1][2]:
        return None
    name, score, _ = matches[0]
    return name, score


def _price_ratio_ok(prompt_price, completion_price, arena_prices, candidate_name, tolerance):
    """True unless we have both an OpenRouter price and an arena.ai price for candidate_name
    and they disagree by more than tolerance on either leg. Missing data of any kind (no arena
    scrape, candidate not priced on arena.ai, no OpenRouter price for this query) means there's
    nothing to check against, so the match is allowed through rather than penalized for a gap
    in a bonus signal."""
    if arena_prices is None or prompt_price is None or completion_price is None:
        return True
    if candidate_name not in arena_prices.index:
        return True
    arena_in, arena_out = arena_prices.loc[candidate_name, ['input_price', 'output_price']]
    if pd.isna(arena_in) or pd.isna(arena_out) or arena_in <= 0 or arena_out <= 0:
        return True
    if prompt_price <= 0 or completion_price <= 0:
        return True
    in_ratio = prompt_price / arena_in
    out_ratio = completion_price / arena_out
    worst = max(in_ratio, 1 / in_ratio, out_ratio, 1 / out_ratio)
    return worst <= tolerance


def _candidates_for_provider(provider, score_df):
    """Narrows score_df to the same organization as provider (falling back to the full
    leaderboard if nothing matches -- an unusable filter is worse than no filter), returning
    the candidates alongside the normalized provider key EFFORT_SIBLING_WORDS/LMARENA_ORG_ALIASES
    are keyed by."""
    provider_norm = normalize_org(provider)
    org_mask = score_df['organization'].apply(lambda org: orgs_match(provider_norm, org))
    return (score_df[org_mask] if org_mask.any() else score_df), provider_norm


def orgs_match(provider_norm, organization):
    org_norm = normalize_org(organization)
    if not provider_norm or not org_norm:
        return False
    if LMARENA_ORG_ALIASES.get(provider_norm) == org_norm:
        return True
    return provider_norm in org_norm or org_norm in provider_norm


def normalize_lmarena_df(df_scores):
    """Cleans a raw LM Arena leaderboard DataFrame (as returned by lmarena_download.download_leaderboard,
    or read straight from one of its CSVs) into the organization/model_name/score shape that
    best_match_score() expects."""
    df_scores = df_scores.dropna(subset=['model_name']).copy()
    df_scores['organization'] = df_scores['organization'].fillna('')
    df_scores['model_name'] = df_scores['model_name'].str.lower().apply(canonicalize_version_numbers)
    return df_scores[['organization', 'model_name', 'score']]


def normalize_arena_prices(df_prices):
    """Cleans a raw arena.ai price DataFrame (as returned by arena_price.fetch_arena_prices)
    into an index keyed the same way normalize_lmarena_df()'s model_name column is, so it can
    be looked up with the exact candidate name best_match_score() matched against -- no fuzzy
    join between the two sources, just an exact key lookup that simply misses (and is treated
    as "no price data") if arena.ai's wording ever drifts from the leaderboard dataset's."""
    df_prices = df_prices.dropna(subset=['model_name']).copy()
    df_prices['model_name'] = df_prices['model_name'].str.lower().apply(canonicalize_version_numbers)
    df_prices = df_prices.drop_duplicates(subset='model_name', keep='first')
    return df_prices.set_index('model_name')[['input_price', 'output_price']]


def best_match_score(
    full_model_name,
    score_df,
    prompt_price=None,
    completion_price=None,
    arena_prices=None,
    price_tolerance=PRICE_MISMATCH_TOLERANCE,
):
    """Score-only view of _best_match -- see its docstring for the matching rules."""
    match = _best_match(full_model_name, score_df, prompt_price, completion_price, arena_prices, price_tolerance)
    return match[1] if match else None


def _best_match(
    full_model_name,
    score_df,
    prompt_price=None,
    completion_price=None,
    arena_prices=None,
    price_tolerance=PRICE_MISMATCH_TOLERANCE,
):
    """Finds the best-matching LM Arena (candidate_name, score) pair for an OpenRouter model
    id, bridging OpenRouter's
    `provider/slug` ids and LM Arena's own model naming (which adds date stamps, effort suffixes
    like '-high'/'-thinking-32k', etc.).

    OpenRouter's rolling '-latest' aliases (e.g. 'anthropic/claude-opus-latest') and the
    unmarked aliases in UNPINNED_ALIASES are refused outright: which pinned version they
    currently point at isn't knowable from the id itself, so guessing one is worse than
    reporting no score at all.

    Matching happens in three stages, all on exact word/number tokens -- there is no
    character-level fuzzy scoring anywhere, deliberately: it makes short, undecorated brand
    names (e.g. 'sonar-pro') look like a near-perfect match for an unrelated model that merely
    shares most letters (e.g. 'solar-pro4') purely on character resemblance, with nothing in
    the name actually in common.

    1. Exact: the canonicalized slug equals a candidate's canonicalized name exactly. Always
       wins, and is the only stage exempt from the price check below -- two listings of the
       literal same model id can legitimately have different prices (different host, markup).
    2. Prefix: the slug is a string-prefix of the candidate (so a decorated LM Arena entry,
       e.g. 'claude-opus-4-6-thinking', still matches a plain query), guarded so the candidate
       doesn't just continue the same version number one digit further (see
       _prefix_boundary_safe) -- otherwise a bare 'claude-opus-4-6' would prefix-match
       'claude-opus-4-67', or 'mistral-medium-3' would prefix-match 'mistral-medium-3.5'.
    3. Token superset: the slug's tokens (see _tokenize) are all present in the candidate's,
       which the candidate may have extra decorations beyond. This is what lets LM Arena's
       space-separated, suffix-decorated names ('Claude Sonnet 4.5 Thinking') match a
       dash-separated OpenRouter slug without any character fuzziness.

    Both stage 2 and 3 can have more than one surviving candidate (e.g. a bare 'gpt-5' against
    both 'gpt-5-high' and 'gpt-5-medium', one extra token each) -- see
    _closest_unique_candidate: the closest (fewest extra tokens) wins only if it's uniquely
    closest, otherwise which one the query means is genuinely ambiguous and the match is
    rejected rather than resolved by picking whichever has the higher arena score.

    Both stage 2 and 3 additionally reject any candidate whose only-on-the-candidate-side
    tokens include a word in DENIED_UNREQUESTED_TOKENS (see its docstring) -- e.g. a bare
    'moonshotai/kimi-k2' must not land on 'kimi-k2-turbo', a separately-priced faster tier the
    query never asked for.

    Finally, if prompt_price/completion_price and arena_prices are supplied, a stage-2 or
    stage-3 match is rejected when arena.ai's own displayed price for the matched candidate
    disagrees with OpenRouter's price by more than price_tolerance on either leg (see
    _price_ratio_ok) -- two independently-sourced prices for what's supposed to be the same
    model shouldn't be wildly apart. Missing price data on either side is not treated as a
    mismatch; the check simply doesn't fire."""
    provider, _, slug = full_model_name.lower().partition('/')
    slug = canonicalize_version_numbers(slug.split(':', 1)[0])  # drop ':batch' etc., 3.5/4-6 -> 3p5/4p6

    if 'latest' in re.findall(r'[a-z0-9]+', slug) or full_model_name.lower().split(':', 1)[0] in UNPINNED_ALIASES:
        return None

    candidates, _ = _candidates_for_provider(provider, score_df)
    names = candidates['model_name']

    exact = candidates[names == slug]
    if not exact.empty:
        return slug, exact['score'].max()

    slug_tokens = _tokenize(slug)

    prefix_matches = [
        (name, score, len(_tokenize(name) - slug_tokens))
        for name, score in zip(names, candidates['score'], strict=True)
        if name.startswith(slug)
        and _prefix_boundary_safe(name, len(slug))
        and not _has_unrequested_denied_token(slug_tokens, name)
    ]
    closest = _closest_unique_candidate(prefix_matches)
    if prefix_matches:
        if closest is None:
            return None  # ambiguous -- multiple equally-decorated candidates, don't guess
        name, score = closest
        if _price_ratio_ok(prompt_price, completion_price, arena_prices, name, price_tolerance):
            return name, score
        return None

    if not slug_tokens:
        return None

    superset_matches = [
        (name, score, len(_tokenize(name) - slug_tokens))
        for name, score in zip(names, candidates['score'], strict=True)
        if slug_tokens <= _tokenize(name) and not _has_unrequested_denied_token(slug_tokens, name)
    ]
    closest = _closest_unique_candidate(superset_matches)
    if closest is None:
        return None
    name, score = closest
    if _price_ratio_ok(prompt_price, completion_price, arena_prices, name, price_tolerance):
        return name, score
    return None


def _effort_siblings(full_model_name, score_df, claimed_names):
    """Arena entries not already claimed by primary matching (claimed_names) whose tokens
    equal this OpenRouter row's own slug tokens once its provider's whitelisted effort words
    (see EFFORT_SIBLING_WORDS) are removed -- i.e. entries that differ only by an effort-level
    dial, so this row's OpenRouter price is still the correct price for them. Unlike
    _best_match, ties are not rejected here: multiple genuinely different effort tiers of the
    same product (e.g. '-high' and '-max') are each their own valid sibling, not a single
    ambiguous slot to pick one from. Returns a list of (candidate_name, score, extra_tokens)."""
    provider, _, slug = full_model_name.lower().partition('/')
    slug = canonicalize_version_numbers(slug.split(':', 1)[0])
    candidates, provider_norm = _candidates_for_provider(provider, score_df)
    effort_words = EFFORT_SIBLING_WORDS.get(provider_norm)
    if not effort_words:
        return []

    slug_tokens = _tokenize(slug)
    siblings = []
    for name, score in zip(candidates['model_name'], candidates['score'], strict=True):
        if name in claimed_names:
            continue
        name_tokens = _tokenize(name)
        extra = name_tokens - slug_tokens
        if extra and (name_tokens - effort_words) == slug_tokens:
            siblings.append((name, score, extra))
    return siblings


def _cost_anchors(matched_scores):
    """Self-calibrating (low_score, high_score) bounds for compute_scaled_cost_estimate's linear
    interpolation, from the COST_SCALE_LOW_PERCENTILE/COST_SCALE_HIGH_PERCENTILE percentiles of
    matched_scores (this report's own lm_arena_score column, before any effort sibling rows --
    see EFFORT_SIBLING_WORDS -- so one product's extra duplicated row can't skew the bounds
    toward itself). Returns (None, None) when there aren't enough distinct scores to support a
    meaningful spread (compute_scaled_cost_estimate already treats None bounds as "leave
    scaled_cost_estimate blank")."""
    valid = matched_scores.dropna()
    if valid.nunique() < 2:
        return None, None
    low_score, high_score = valid.quantile([COST_SCALE_LOW_PERCENTILE, COST_SCALE_HIGH_PERCENTILE])
    return low_score, high_score


def compute_cost_estimate(prompt_price, completion_price):
    """Weighted API price for a rough (coding/web-dev-flavored) run: 80% prompt, 20% completion."""
    return round(0.8 * prompt_price + 0.2 * completion_price, 3)


def compute_scaled_cost_estimate(lm_arena_score, cost_estimate, low_score, high_score):
    """Linearly scales cost_estimate between a COST_SCALE_MAX_FACTOR penalty at low_score and a
    1/COST_SCALE_MAX_FACTOR discount at high_score, extrapolating the same slope for scores
    beyond either bound (deliberately unclamped -- see the COST_SCALE_MAX_FACTOR comment)."""
    if pd.isna(lm_arena_score) or low_score is None or high_score is None or high_score <= low_score:
        return float('nan')

    low_mult, high_mult = COST_SCALE_MAX_FACTOR, 1 / COST_SCALE_MAX_FACTOR
    multiplier = low_mult + (high_mult - low_mult) * (lm_arena_score - low_score) / (high_score - low_score)
    return round(cost_estimate * multiplier, 3)


def enrich_with_lmarena(data_models, score_df, arena_prices=None):
    """Adds lm_arena_score, lm_arena_model_name, cost_estimate and scaled_cost_estimate columns
    to an OpenRouter pricing DataFrame (as returned by or_model_filtering.get_models), and
    reorders the columns for display. score_df should come from normalize_lmarena_df();
    arena_prices, if supplied, should come from normalize_arena_prices() and enables the
    price-mismatch check in best_match_score().

    lm_arena_model_name records exactly which (normalized) LM Arena candidate lm_arena_score
    came from; report_pipeline turns it into the visible lm_arena_entry column.

    Also appends one extra row per "effort sibling" found (see _effort_siblings): an LM Arena
    entry that differs from an already-priced OpenRouter row only by a whitelisted
    effort-level word (EFFORT_SIBLING_WORDS), so that row's price is duplicated onto it instead
    of the entry being silently dropped. A sibling row keeps its source row's full_model_name
    unchanged (it's still the same OpenRouter listing) -- lm_arena_model_name and
    lm_arena_score are the only columns that differ, which is what tells the rows apart."""
    data_models = data_models.copy()
    matches = data_models.apply(
        lambda row: _best_match(
            row['full_model_name'], score_df, row['prompt_price'], row['completion_price'], arena_prices
        ),
        axis=1,
    )
    data_models['lm_arena_score'] = matches.apply(lambda match: match[1] if match else float('nan'))
    data_models['lm_arena_model_name'] = matches.apply(lambda match: match[0] if match else None)
    claimed_names = {match[0] for match in matches if match is not None}

    low_score, high_score = _cost_anchors(data_models['lm_arena_score'])

    data_models['cost_estimate'] = compute_cost_estimate(data_models['prompt_price'], data_models['completion_price'])
    data_models['scaled_cost_estimate'] = data_models.apply(
        lambda row: compute_scaled_cost_estimate(row['lm_arena_score'], row['cost_estimate'], low_score, high_score),
        axis=1,
    )

    sibling_rows = []
    for _, row in data_models.iterrows():
        for name, score, _extra in _effort_siblings(row['full_model_name'], score_df, claimed_names):
            sibling = row.copy()
            sibling['lm_arena_score'] = score
            sibling['lm_arena_model_name'] = name
            sibling['scaled_cost_estimate'] = compute_scaled_cost_estimate(
                score, row['cost_estimate'], low_score, high_score
            )
            sibling_rows.append(sibling)
    if sibling_rows:
        data_models = pd.concat([data_models, pd.DataFrame(sibling_rows)], ignore_index=True)

    data_models = data_models[
        [
            'full_model_name',
            'lm_arena_score',
            'lm_arena_model_name',
            'prompt_price',
            'completion_price',
            'cost_estimate',
            'scaled_cost_estimate',
            'context_length',
            'max_completion_tokens',
            'provider',
        ]
    ]
    return data_models.round(3)  # belt-and-suspenders: no long floating-point tails in any numeric column


def load_lmarena_scores(subset, csv_dir='.'):
    """Loads the most recently downloaded lmarena_<subset>_*.csv (from csv_dir, the demo's own folder
    by default) into the organization/model_name/score shape of normalize_lmarena_df(), ready for
    enrich_with_lmarena()."""
    pattern = os.path.join(csv_dir, f'lmarena_{subset}_*.csv')
    matches = sorted(glob.glob(pattern))
    if not matches:
        print(
            f"Warning: no LM Arena CSV found for subset '{subset}' in '{csv_dir}'. "
            f'Run `python3 <path-to>/components/lmarena/lmarena_download.py --subset {subset}` '
            f'from that folder first.'
        )
        return pd.DataFrame(columns=['organization', 'model_name', 'score'])

    return normalize_lmarena_df(pd.read_csv(matches[-1], sep=';'))


def best_entry_per_model(data_models):
    """Collapses enrich_with_lmarena()'s effort-sibling rows to one row per full_model_name, keeping
    its best-scoring exact LM Arena entry (never a blend), for model pickers that list each
    OpenRouter model once. Keeps get_models()' row order and drops the internal lm_arena_model_name."""
    best = data_models.sort_values('lm_arena_score', ascending=False, na_position='last', kind='stable')
    return best.drop_duplicates('full_model_name').sort_index().drop(columns='lm_arena_model_name')
