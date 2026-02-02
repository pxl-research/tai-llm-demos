"""
Settings Modal Component: Model selection and configuration.
"""
from typing import Callable

from nicegui import ui
from utils.model_filtering import get_models


class SettingsModal:
    """Settings modal for model selection and configuration."""

    def __init__(self, on_model_change: Callable, on_settings_change: Callable):
        """
        Initialize settings modal.

        Args:
            on_model_change: Callback when model is changed
            on_settings_change: Callback when settings are changed
        """
        self.on_model_change = on_model_change
        self.on_settings_change = on_settings_change
        self.dialog = None
        self.current_model = 'anthropic/claude-haiku-4.5'
        self.temperature = 0.7
        self.all_models = []  # Store loaded models for search filtering
        self.selected_model_data = None  # Store full model data for Details tab
        self.details_container = None  # Reference to details container for updates
        self.tabs = None  # Reference to tabs for switching
        self.details_tab = None  # Reference to details tab for switching

    def build_ui(self):
        """Build settings modal UI."""
        # Add custom CSS for enhanced visual styling
        ui.add_head_html('''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap');

        .model-card {
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .model-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
        }
        .model-name {
            font-family: 'IBM Plex Mono', monospace;
        }
        .metric-tile {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            padding: 8px;
        }
        .provider-badge {
            background: linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234));
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .price-cheap {
            color: rgb(22, 163, 74);
        }
        .price-moderate {
            color: rgb(217, 119, 6);
        }
        .price-expensive {
            color: rgb(220, 38, 38);
        }
        .search-input-loading {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .search-input-ready {
            animation: searchReady 0.4s ease;
        }
        @keyframes searchReady {
            0% { border-color: #e5e7eb; }
            50% { border-color: rgb(79, 70, 229); box-shadow: 0 0 8px rgba(79, 70, 229, 0.3); }
            100% { border-color: #e5e7eb; }
        }
        /* Selected indicator dot */
        .selected-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: linear-gradient(135deg, rgb(79, 70, 229), rgb(147, 51, 234));
            animation: pulse-dot 2s ease-in-out infinite;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.1); }
        }
        /* Metric dividers */
        .metric-divider {
            width: 1px;
            height: 32px;
            background: linear-gradient(to bottom,
                transparent 0%,
                rgba(79, 70, 229, 0.2) 20%,
                rgba(147, 51, 234, 0.2) 80%,
                transparent 100%
            );
        }
        /* Pricing separator */
        .pricing-separator {
            width: 100%;
            height: 1px;
            background: linear-gradient(to right,
                transparent 0%,
                rgba(79, 70, 229, 0.15) 20%,
                rgba(147, 51, 234, 0.15) 80%,
                transparent 100%
            );
            margin: 8px 0;
        }
        </style>
        ''')

        with ui.dialog().props('role="dialog" aria-labelledby="settings-title"') as dialog:
            with ui.card().classes('w-full max-w-2xl max-h-[80vh] overflow-y-auto'):
                ui.label('Settings').classes('text-h6 font-bold').props('id="settings-title"')

                with ui.tabs().classes('w-full') as tabs:
                    model_tab = ui.tab('Model Selection')
                    details_tab = ui.tab('Model Details')

                # Store tabs reference for switching
                self.tabs = tabs
                self.details_tab = details_tab

                with ui.tab_panels(tabs, value=model_tab).classes('w-full'):
                    # Model Selection Tab
                    with ui.tab_panel(model_tab):
                        self._build_model_selection()

                    # Model Details Tab
                    with ui.tab_panel(details_tab):
                        self._build_model_details()

                # Buttons
                with ui.row().classes('justify-end gap-2 mt-4 w-full'):
                    ui.button('Cancel', on_click=lambda: dialog.close()).props('flat aria-label="Cancel and close settings"')
                    ui.button(
                        'Save',
                        on_click=lambda: self._save_settings(dialog)
                    ).props('unelevated aria-label="Save settings and apply changes"')

        self.dialog = dialog
        return dialog

    def _build_model_selection(self):
        """Build model selection UI with autocomplete search."""
        ui.label('Select Model').classes('text-h6 font-bold')

        # Container for search and results
        with ui.column().classes('w-full gap-2 mt-4'):

            # Loading indicator label (visible until models load)
            loading_indicator = ui.label('⏳ Loading models...').classes('text-sm text-gray-600 mb-1')

            # Search input with icon - initially disabled until models load
            search_input = ui.input(
                placeholder='Search models...'
            ).classes('w-full search-input-loading').props('outlined clearable disabled aria-label="Search models" role="searchbox"')
            search_input.props('prepend-inner-icon=search')

            # Loading state
            loading_container = ui.column().classes('w-full items-center py-8')
            with loading_container:
                ui.spinner(size='lg', color='indigo')
                ui.label('Loading models...').classes('text-sm text-gray-600 mt-2')

            # Results container (hidden initially)
            results_container = ui.column().classes(
                'w-full gap-2 max-h-[450px] overflow-y-auto p-2'
            )
            results_container.visible = False

            # Function to select a model
            def select_model(model_data):
                self.current_model = model_data['full_model_name']
                self.selected_model_data = model_data  # Store full model data
                self.tabs.set_value(self.details_tab)  # Switch to Model Details tab
                self._update_details_display()  # Update details tab content

            # Wire up search filtering - set up handler immediately
            def on_search(e):
                if self.all_models:  # Only filter if models are loaded
                    self._filter_results(e.value, results_container, self.all_models, select_model)

            search_input.on_value_change(on_search)

            # Auto-load models on init
            async def load_models():
                try:
                    models_df = get_models(
                        tools_only=True,           # Only models with tool calling support
                        image_only=False,
                        min_context=64000,         # Require 64K+ context
                        max_completion_price=100,  # Allow higher price for quality models
                        max_prompt_price=50,       # Allow higher price for quality models
                        skip_free=True,            # Exclude free/rate-limited models
                        skip_experimental=True     # Exclude beta/experimental models
                    )

                    # Convert DataFrame to list of dicts for easier template iteration
                    self.all_models = models_df.to_dict('records')

                    # Hide loading, show results
                    loading_container.visible = False
                    results_container.visible = True

                    # Hide loading indicator and enable search
                    loading_indicator.visible = False
                    search_input.classes(remove='search-input-loading', add='search-input-ready')
                    search_input.props(remove='disabled')
                    search_input.set_value('')  # Clear any input during loading

                    # Initial display of all models
                    self._filter_results('', results_container, self.all_models, select_model)

                    # Set initial selected model data if current model exists in the list
                    if self.current_model:
                        current_model_info = [
                            m for m in self.all_models
                            if m['full_model_name'] == self.current_model
                        ]
                        if current_model_info:
                            self.selected_model_data = current_model_info[0]
                            self._update_details_display()

                except Exception as e:
                    loading_container.clear()
                    with loading_container:
                        ui.label(f'Error loading models: {str(e)}').classes('text-red-600')

            # Trigger initial load
            ui.timer(0.1, load_models, once=True)

    def _build_model_details(self):
        """Build model details tab with reactive updates."""
        # Create container for dynamic content
        self.details_container = ui.column().classes('w-full gap-4 p-4')

        # Initial display
        self._update_details_display()

    def _update_details_display(self):
        """Update model details display reactively."""
        if self.details_container is None:
            return

        self.details_container.clear()

        with self.details_container:
            if self.selected_model_data is None:
                # Empty state
                with ui.column().classes('w-full items-center justify-center py-16'):
                    ui.icon('search', size='4rem').classes('text-gray-300')
                    ui.label('No model selected').classes('text-lg text-gray-500 mt-4')
                    ui.label('Select a model from the Model Selection tab').classes('text-sm text-gray-400')
            else:
                # Show full details using horizontal compact layout
                self._render_model_details(self.selected_model_data)


    def _save_settings(self, dialog):
        """Save settings and close dialog."""
        self.on_model_change(self.current_model)
        self.on_settings_change({'temperature': self.temperature})
        dialog.close()

    def show(self):
        """Show the settings modal."""
        if self.dialog:
            self.dialog.open()

    def close(self):
        """Close the settings modal."""
        if self.dialog:
            self.dialog.close()

    def _get_price_color(self, price: float) -> str:
        """
        Return CSS class for price tier color coding.

        Args:
            price: Price per 1M tokens

        Returns:
            CSS class name for color
        """
        if price < 0.50:  # Cheap: under $0.50 per 1M
            return 'price-cheap'
        elif price < 2.00:  # Moderate: $0.50-$2.00 per 1M
            return 'price-moderate'
        else:  # Expensive: over $2.00 per 1M
            return 'price-expensive'

    def _filter_results(self, search_text: str, results_container, all_models: list, on_click_callback=None):
        """
        Filter model results based on search text.

        Args:
            search_text: User's search input
            results_container: Container to populate with filtered results
            all_models: List of all available models
            on_click_callback: Optional callback for when a model card is clicked
        """
        results_container.clear()

        if not search_text:
            filtered = all_models
        else:
            search_lower = search_text.lower()
            filtered = [
                m for m in all_models
                if search_lower in m['full_model_name'].lower()
                or search_lower in m['provider'].lower()
            ]

        # Group by provider
        providers = {}
        for model in filtered:
            provider = model['provider']
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)

        # Display grouped results
        with results_container:
            if not filtered:
                ui.label('No models found').classes('text-gray-500 italic p-4')
            else:
                for provider, models in sorted(providers.items()):
                    # Provider header
                    ui.label(provider).classes('text-sm font-semibold text-gray-700 mt-2 mb-1')
                    # Models for this provider
                    for model in models:
                        self._create_model_card(model, on_click_callback)

    def _create_model_card(self, model_data: dict, on_click_callback=None):
        """
        Create a clickable model card.

        Args:
            model_data: Dictionary with model information
            on_click_callback: Optional callback for when card is clicked
        """
        with ui.card().classes(
            'model-card w-full bg-white border border-gray-200 p-2 cursor-pointer'
        ).props('role="button" tabindex="0"') as card:
            with ui.row().classes('w-full justify-between items-center'):
                # Provider badge
                ui.label(model_data['provider']).classes('provider-badge')

                # Quick stats - show input/output costs
                with ui.row().classes('gap-2 text-xs text-gray-600'):
                    prompt_price = model_data['prompt_price']  # Already per-1M
                    ui.label(f"In: ${prompt_price:.2f}").classes('font-mono')
                    ui.label('•')
                    completion_price = model_data['completion_price']  # Already per-1M
                    ui.label(f"Out: ${completion_price:.2f}").classes('font-mono')

            # Model name
            ui.label(model_data['full_model_name']).classes(
                'model-name text-sm font-semibold mt-2'
            )

            # Attach click handler if provided
            if on_click_callback:
                card.on('click', lambda m=model_data: on_click_callback(m))

    def _render_model_details(self, model_info: dict):
        """
        Render model details with compact, inline metrics.

        Args:
            model_info: Dictionary with model information
        """
        # Header row: provider badge + selected indicator
        with ui.row().classes('w-full justify-between items-center mb-3'):
            ui.label(model_info['provider']).classes('provider-badge')
            with ui.row().classes('gap-1 items-center'):
                ui.element('div').classes('selected-dot')
                ui.label('Selected').classes('text-xs text-indigo-600 font-semibold tracking-wide')

        # Model name with distinctive styling
        ui.label(model_info['full_model_name']).classes(
            'model-name text-base font-semibold mb-4 text-gray-800'
        ).style('letter-spacing: -0.02em;')

        # Compact metrics display - single row with dividers
        with ui.row().classes('w-full items-center gap-3 mb-3'):
            # Context length metric
            with ui.column().classes('gap-0.5 flex-1'):
                ui.label('CONTEXT').classes('text-[10px] font-bold text-gray-500 tracking-wider')
                with ui.row().classes('items-baseline gap-1'):
                    ui.label(f"{model_info['context_length']:,}").classes(
                        'text-lg font-bold text-gray-900 font-mono'
                    )
                    ui.label('tokens').classes('text-xs text-gray-500')

            # Vertical divider
            ui.element('div').classes('metric-divider')

            # Max completion metric
            with ui.column().classes('gap-0.5 flex-1'):
                ui.label('MAX OUTPUT').classes('text-[10px] font-bold text-gray-500 tracking-wider')
                with ui.row().classes('items-baseline gap-1'):
                    ui.label(f"{model_info['max_completion_tokens']:,}").classes(
                        'text-lg font-bold text-gray-900 font-mono'
                    )
                    ui.label('tokens').classes('text-xs text-gray-500')

        # Pricing section with visual hierarchy
        ui.element('div').classes('pricing-separator')

        with ui.row().classes('w-full items-center gap-3 mt-3'):
            # Prompt pricing
            prompt_price = model_info['prompt_price']
            prompt_color_class = self._get_price_color(prompt_price)

            with ui.column().classes('gap-0.5 flex-1'):
                ui.label('INPUT COST').classes('text-[10px] font-bold text-gray-500 tracking-wider')
                with ui.row().classes('items-baseline gap-1'):
                    ui.label(f"${prompt_price:.2f}").classes(
                        f'text-lg font-bold font-mono {prompt_color_class}'
                    )
                    ui.label('/1M').classes('text-xs text-gray-500 font-mono')

            # Vertical divider
            ui.element('div').classes('metric-divider')

            # Completion pricing
            completion_price = model_info['completion_price']
            completion_color_class = self._get_price_color(completion_price)

            with ui.column().classes('gap-0.5 flex-1'):
                ui.label('OUTPUT COST').classes('text-[10px] font-bold text-gray-500 tracking-wider')
                with ui.row().classes('items-baseline gap-1'):
                    ui.label(f"${completion_price:.2f}").classes(
                        f'text-lg font-bold font-mono {completion_color_class}'
                    )
                    ui.label('/1M').classes('text-xs text-gray-500 font-mono')

        # Temperature section (merged from Settings tab)
        ui.separator().classes('my-6')

        ui.label('Temperature').classes('text-sm font-bold text-gray-700 mb-2')
        temp_label = ui.label(f'{self.temperature:.1f}').classes('text-lg font-mono font-bold text-indigo-600 mb-2')

        def on_temp_change(e):
            self.temperature = e.value
            temp_label.text = f'{self.temperature:.1f}'

        ui.slider(
            min=0.0,
            max=2.0,
            step=0.1,
            value=self.temperature,
            on_change=on_temp_change
        ).classes('w-full').props('color=indigo')

        with ui.row().classes('w-full justify-between mt-2 mb-4'):
            ui.label('Deterministic').classes('text-xs text-gray-500 italic')
            ui.label('Creative').classes('text-xs text-gray-500 italic')

        ui.label(
            'Controls randomness: Lower values (0.0-0.3) produce consistent outputs. '
            'Higher values (1.0+) produce more creative responses.'
        ).classes('text-xs italic text-gray-600 leading-relaxed')
