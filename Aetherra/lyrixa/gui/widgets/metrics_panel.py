#!/usr/bin/env python3
"""
Compact reusable right-side metrics panel for Lyrixa UI.
Extracted from main_window to improve maintainability.
"""

from typing import Any, Dict, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class MetricsPanel(QFrame):
    """Right-side live metrics/status panel."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(280)
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📊 Live Metrics")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00ff88;
                padding: 15px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
            """
        )
        layout.addWidget(title)

        self.metrics_widgets: Dict[str, QFrame] = {}
        # Seed default cards
        defaults = [
            ("Memory Load", "45%", "#00ff88"),
            ("CPU Usage", "23%", "#0078d4"),
            ("Agents Active", "7", "#ff6b00"),
            ("Plugins Loaded", "12", "#9d4edd"),
        ]
        for name, value, color in defaults:
            metric_widget = self._create_metric_widget(name, value, color)
            layout.addWidget(metric_widget)
            self.metrics_widgets[name] = metric_widget

        layout.addStretch()

    def _create_metric_widget(self, name: str, value: str, color: str) -> QFrame:
        widget = QFrame()
        widget.setObjectName(f"metric_{name.replace(' ', '_').lower()}")
        widget.setStyleSheet(
            """
            QFrame {
                background: rgba(26, 26, 26, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                margin: 5px 0;
            }
            """
        )
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(
            f"color: {color}; font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(name_label)
        layout.addWidget(value_label)
        return widget

    def update_values(self, metrics: Mapping[str, Any]):
        """Update visible values on the cards when new metrics arrive."""
        mapping = {
            "memory_load": "Memory Load",
            "cpu_usage": "CPU Usage",
            "agents_active": "Agents Active",
            "plugins_loaded": "Plugins Loaded",
        }
        for key, display in mapping.items():
            if key in metrics and display in self.metrics_widgets:
                frame = self.metrics_widgets[display]
                value_label = frame.findChild(QLabel, "value")
                if value_label:
                    val = metrics[key]
                    if isinstance(val, (int, float)) and "Usage" in display:
                        value_label.setText(f"{int(val)}%")
                    else:
                        value_label.setText(str(val))
