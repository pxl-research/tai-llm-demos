import pandas as pd

# Color anchors for the report's gradient columns (red -> yellow -> green).
SCORE_RED = 1410
SCORE_YELLOW = 1440
SCORE_GREEN = 1470

# Price column anchors (green -> yellow -> red): green = cheap/good, red = expensive/bad.
PROMPT_PRICE_GREEN, PROMPT_PRICE_YELLOW, PROMPT_PRICE_RED = 1, 1.5, 5
COMPLETION_PRICE_GREEN, COMPLETION_PRICE_YELLOW, COMPLETION_PRICE_RED = 2.5, 7.5, 20
COST_ESTIMATE_GREEN, COST_ESTIMATE_YELLOW, COST_ESTIMATE_RED = 1, 2, 5  # shared by cost_estimate and scaled_cost_estimate

RED = (240, 100, 100)
YELLOW = (255, 235, 132)
GREEN = (99, 190, 123)

# column -> (low, mid, high, low_color, mid_color, high_color) passed straight to _gradient_color
COLUMN_GRADIENTS = {
    'lm_arena_score': (SCORE_RED, SCORE_YELLOW, SCORE_GREEN, RED, YELLOW, GREEN),
    'prompt_price': (PROMPT_PRICE_GREEN, PROMPT_PRICE_YELLOW, PROMPT_PRICE_RED, GREEN, YELLOW, RED),
    'completion_price': (COMPLETION_PRICE_GREEN, COMPLETION_PRICE_YELLOW, COMPLETION_PRICE_RED, GREEN, YELLOW, RED),
    'cost_estimate': (COST_ESTIMATE_GREEN, COST_ESTIMATE_YELLOW, COST_ESTIMATE_RED, GREEN, YELLOW, RED),
    'scaled_cost_estimate': (COST_ESTIMATE_GREEN, COST_ESTIMATE_YELLOW, COST_ESTIMATE_RED, GREEN, YELLOW, RED),
}

TABLE_STYLES = [
    {'selector': 'table, th, td', 'props': [('font-family', 'Segoe UI, Helvetica, Arial, sans-serif')]},
    {'selector': 'th, td', 'props': [('padding', '6px 14px')]},
]

# column -> decimal places to display
NUMBER_FORMATS = {
    'lm_arena_score': '{:.1f}',
    'prompt_price': '{:.2f}',
    'completion_price': '{:.2f}',
    'cost_estimate': '{:.2f}',
    'scaled_cost_estimate': '{:.2f}',
    'context_length': '{:.0f}',
    'max_completion_tokens': '{:.0f}',
}


def _lerp_color(color_a, color_b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a + (b - a) * t) for a, b in zip(color_a, color_b))


def _to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def _gradient_color(value, low, mid, high, low_color, mid_color, high_color):
    """Interpolates a background-color CSS declaration for value across a
    low -> mid -> high three-point color scale, clamped at both ends."""
    if pd.isna(value):
        return ''
    if value <= low:
        rgb = low_color
    elif value >= high:
        rgb = high_color
    elif value <= mid:
        rgb = _lerp_color(low_color, mid_color, (value - low) / (mid - low))
    else:
        rgb = _lerp_color(mid_color, high_color, (value - mid) / (high - mid))
    return f'background-color: {_to_hex(rgb)}'


def render_html_report(data_models):
    """Returns an HTML string rendering of data_models with color-scaled lm_arena_score and
    price columns, per the low -> mid -> high anchors defined in COLUMN_GRADIENTS."""
    styler = data_models.style.hide(axis='index')
    styler = styler.set_table_styles(TABLE_STYLES)
    styler = styler.format({col: fmt for col, fmt in NUMBER_FORMATS.items() if col in data_models.columns},
                           na_rep='')
    for column, anchors in COLUMN_GRADIENTS.items():
        if column in data_models.columns:
            styler = styler.map(lambda v, anchors=anchors: _gradient_color(v, *anchors), subset=[column])
    return styler.to_html()


def write_html_report(data_models, out_path):
    with open(out_path, 'wt') as fp:
        fp.write(render_html_report(data_models))
    return out_path
