"""
PXL brand theme: colors and fonts from https://www.pxl.be/over-pxl/huisstijl/kleuren-en-letters/

The guide specifies Museo Sans for body text, which is a licensed font we don't have a
web-font kit for, so Poppins stands in until one is available.
"""
from nicegui import ui

PXL_BLACK = '#030203'
PXL_BLACK_SOFT = '#1c1c1c'
PXL_WHITE = '#ffffff'
PXL_GOLD = '#ae9a64'
PXL_GOLD_SOFT = 'rgba(174, 154, 100, 0.18)'


def inject_pxl_theme():
    """Load PXL brand fonts/colors and apply them as the app-wide defaults.

    Uses ui.colors() rather than a hand-rolled `:root { --q-primary }` override:
    Quasar sets its brand CSS vars at runtime, which clobbers a plain CSS rule --
    ui.colors() is NiceGui's supported hook into that same mechanism.
    """
    ui.colors(primary=PXL_GOLD, dark=PXL_BLACK)

    ui.add_head_html(f'''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@700;900&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --pxl-black: {PXL_BLACK};
                --pxl-gold: {PXL_GOLD};
            }}
            body {{
                font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .pxl-heading {{
                font-family: 'Raleway', sans-serif;
                font-weight: 900;
            }}
            button:focus-visible,
            input:focus-visible,
            textarea:focus-visible {{
                outline: 2px solid var(--pxl-gold) !important;
                outline-offset: 2px;
            }}
            .q-card:focus-visible {{
                outline: 2px solid var(--pxl-gold);
                box-shadow: 0 0 0 3px {PXL_GOLD_SOFT};
            }}
        </style>
    ''')
