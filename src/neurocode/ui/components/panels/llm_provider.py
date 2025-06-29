#!/usr/bin/env python3
"""
LLM Provider Panel for Neuroplex
================================

Panel for managing LLM providers and configurations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports with fallback
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QComboBox,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QSpinBox,
        QWidget,
    )
except ImportError:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QComboBox,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QSpinBox,
        QWidget,
    )


# Theme colors (inline for now)
class ModernTheme:
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    PRIMARY = "#3b82f6"
    PRIMARY_VARIANT = "#1e40af"
    SECONDARY_VARIANT = "#059669"
    TEXT_PRIMARY = "#ffffff"
    SURFACE_VARIANT = "#2a2a2a"
    BORDER = "#374151"
    CARD = "#1e1e1e"

    @staticmethod
    def get_card_style():
        return f"""
        QWidget {{
            background-color: {ModernTheme.CARD};
            border: 1px solid {ModernTheme.BORDER};
            border-radius: 6px;
            padding: 6px;
        }}
        QPushButton {{
            min-height: 24px;
            padding: 4px 8px;
            font-size: 11px;
        }}
        """


class ModernCard(QWidget):
    """Simple card widget"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(ModernTheme.get_card_style())

        self.content_layout = QWidget()

    def add_widget(self, widget):
        pass  # Simplified for now


class LLMProviderPanel(ModernCard):
    """Panel for managing LLM providers"""

    def __init__(self, llm_manager=None, parent=None):
        super().__init__("🤖 LLM Providers", parent)
        self.llm_manager = llm_manager
        self.init_ui()
        self.update_providers()

    def init_ui(self):
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Active Provider:"))

        self.provider_combo = QComboBox()
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)

        # Model configuration
        config_group = QGroupBox("Model Configuration")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("Temperature:"), 0, 0)
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_value_label = QLabel("0.7")
        self.temp_slider.valueChanged.connect(self.update_temp_label)
        config_layout.addWidget(self.temp_slider, 0, 1)
        config_layout.addWidget(self.temp_value_label, 0, 2)

        config_layout.addWidget(QLabel("Max Tokens:"), 1, 0)
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(1, 8192)
        self.tokens_spin.setValue(2048)
        config_layout.addWidget(self.tokens_spin, 1, 1)

        # Provider status
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {ModernTheme.SUCCESS}; font-size: 16px;")
        self.status_label = QLabel("Connected")
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        # Test connection button
        test_btn = QPushButton("🔍 Test")
        test_btn.clicked.connect(self.test_connection)
        test_btn.setProperty("buttonRole", "secondary")
        test_btn.setMaximumWidth(60)
        status_layout.addWidget(test_btn)

    def update_providers(self):
        """Update available providers from LLM manager"""
        if self.llm_manager:
            try:
                models = self.llm_manager.list_available_models()
                self.provider_combo.clear()
                for model in models:
                    self.provider_combo.addItem(
                        f"{model.get('provider', 'Unknown')}: {model.get('name', 'Unknown')}"
                    )

                if models:
                    self.status_label.setText(f"{len(models)} models available")
                else:
                    self.status_label.setText("No models configured")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.WARNING}; font-size: 16px;"
                    )
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)[:50]}...")
                self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")
        else:
            self.provider_combo.addItems(
                [
                    "OpenAI GPT-4",
                    "OpenAI GPT-3.5",
                    "Anthropic Claude",
                    "Google Gemini",
                    "Local Ollama",
                    "LlamaCpp",
                ]
            )

    def on_provider_changed(self, provider_name):
        """Handle provider selection change"""
        if self.llm_manager:
            try:
                if ": " in provider_name:
                    model_name = provider_name.split(": ")[1]
                    self.llm_manager.set_model(model_name)
                    self.status_label.setText(f"Switched to {model_name}")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.SUCCESS}; font-size: 16px;"
                    )
            except Exception as e:
                self.status_label.setText(f"Switch failed: {str(e)[:30]}...")
                self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")

    def update_temp_label(self, value):
        """Update temperature label"""
        temp_value = value / 100.0
        self.temp_value_label.setText(f"{temp_value:.2f}")

    def test_connection(self):
        """Test connection to current provider"""
        try:
            if self.llm_manager:
                response = self.llm_manager.generate_response("Test connection")
                if response and len(response) > 0:
                    self.status_label.setText("Connection successful!")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.SUCCESS}; font-size: 16px;"
                    )
                else:
                    self.status_label.setText("Connection failed")
                    self.status_indicator.setStyleSheet(
                        f"color: {ModernTheme.ERROR}; font-size: 16px;"
                    )
            else:
                self.status_label.setText("LLM manager not available")
                self.status_indicator.setStyleSheet(
                    f"color: {ModernTheme.WARNING}; font-size: 16px;"
                )
        except Exception as e:
            self.status_label.setText(f"Test failed: {str(e)[:30]}...")
            self.status_indicator.setStyleSheet(f"color: {ModernTheme.ERROR}; font-size: 16px;")
