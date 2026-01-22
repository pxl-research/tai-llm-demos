"""
Settings Modal Component: Model selection and configuration.
"""
from typing import Callable, Optional

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
        self.models_df = None

    def build_ui(self):
        """Build settings modal UI."""
        with ui.dialog() as dialog:
            with ui.card().classes('w-full max-w-2xl'):
                ui.label('Settings').classes('text-h6 font-bold')

                with ui.tabs().classes('w-full') as tabs:
                    model_tab = ui.tab('Model Selection')
                    settings_tab = ui.tab('Advanced Settings')

                with ui.tab_panels(tabs, value=model_tab).classes('w-full'):
                    # Model Selection Tab
                    with ui.tab_panel(model_tab):
                        self._build_model_selection()

                    # Advanced Settings Tab
                    with ui.tab_panel(settings_tab):
                        self._build_advanced_settings()

                # Buttons
                with ui.row().classes('justify-end gap-2 mt-4 w-full'):
                    ui.button('Cancel', on_click=lambda: dialog.close()).props('flat')
                    ui.button(
                        'Save',
                        on_click=lambda: self._save_settings(dialog)
                    ).props('unelevated')

        self.dialog = dialog
        return dialog

    def _build_model_selection(self):
        """Build model selection UI."""
        ui.label('Available Models').classes('font-bold mt-4')

        # Load models button
        def load_models():
            try:
                self.models_df = get_models(
                    tools_only=False,
                    image_only=False,
                    min_context=8000,
                    max_completion_price=50,
                    max_prompt_price=30,
                    skip_free=False,
                    skip_experimental=False
                )
                model_names = self.models_df['full_model_name'].tolist()
                model_select.set_options({name: name for name in model_names})
                status_label.set_text('Models loaded successfully')
            except Exception as e:
                status_label.set_text(f'Error loading models: {str(e)}')

        with ui.row().classes('w-full gap-2'):
            ui.button('Load Available Models', on_click=load_models).props('outline')
            status_label = ui.label('Click "Load Available Models" to see available options')

        # Model dropdown
        def on_model_selected(e):
            self.current_model = e.value
            if self.models_df is not None:
                # Show model details
                model_info = self.models_df[self.models_df['full_model_name'] == e.value]
                if not model_info.empty:
                    info = model_info.iloc[0]
                    details = (
                        f"Context: {info['context_length']} tokens\n"
                        f"Max Completion: {info['max_completion_tokens']} tokens\n"
                        f"Prompt Price: ${info['prompt_price']:.6f}\n"
                        f"Completion Price: ${info['completion_price']:.6f}"
                    )
                    details_label.text = details

        model_select = ui.select(
            {self.current_model: self.current_model},
            value=self.current_model,
            label='Selected Model',
            on_change=on_model_selected
        ).classes('w-full')

        details_label = ui.label('Model details will appear here')

    def _build_advanced_settings(self):
        """Build advanced settings UI."""
        ui.label('Temperature').classes('font-bold mt-4')

        temp_value = ui.label(f'Value: {self.temperature}')

        def on_temp_change(e):
            self.temperature = e.value
            temp_value.text = f'Value: {self.temperature}'

        temp_slider = ui.slider(
            min=0.0,
            max=2.0,
            step=0.1,
            value=self.temperature,
            on_change=on_temp_change
        ).classes('w-full')

        ui.label(
            'Lower values (0.0-0.3) produce more deterministic outputs. '
            'Higher values (1.0+) produce more creative outputs.'
        ).classes('text-caption italic text-gray-600')

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
