#!/usr/bin/env python3
"""
Performance Monitor Panel
========================

Modular component for monitoring system performance and metrics.
"""

import time
from typing import Any, Dict

from ..cards import ModernCard
from ..theme import ModernTheme
from ..utils.qt_imports import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTimer,
    QWidget,
)


class PerformanceMonitorPanel(ModernCard):
    """Panel for monitoring system performance"""

    def __init__(self, parent=None):
        super().__init__("📊 Performance Monitor", parent)
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "response_time": 0.0,
            "requests_per_second": 0.0,
        }
        self.init_ui()
        self.setup_monitoring()

    def init_ui(self):
        """Initialize the user interface"""
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {ModernTheme.SURFACE};
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.PRIMARY};
                border-radius: 3px;
            }}
        """)
        cpu_layout.addWidget(self.cpu_bar)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setMinimumWidth(50)
        cpu_layout.addWidget(self.cpu_label)

        cpu_widget = QWidget()
        cpu_widget.setLayout(cpu_layout)
        self.add_widget(cpu_widget)

        # Memory Usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory:"))
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                text-align: center;
                background-color: {ModernTheme.SURFACE};
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.SECONDARY};
                border-radius: 3px;
            }}
        """)
        memory_layout.addWidget(self.memory_bar)
        self.memory_label = QLabel("0%")
        self.memory_label.setMinimumWidth(50)
        memory_layout.addWidget(self.memory_label)

        memory_widget = QWidget()
        memory_widget.setLayout(memory_layout)
        self.add_widget(memory_widget)

        # Performance stats grid
        stats_layout = QGridLayout()

        stats_layout.addWidget(QLabel("Response Time:"), 0, 0)
        self.response_time_label = QLabel("0ms")
        self.response_time_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.response_time_label, 0, 1)

        stats_layout.addWidget(QLabel("Requests/sec:"), 1, 0)
        self.rps_label = QLabel("0")
        self.rps_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.rps_label, 1, 1)

        stats_layout.addWidget(QLabel("Uptime:"), 2, 0)
        self.uptime_label = QLabel("0s")
        self.uptime_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        stats_layout.addWidget(self.uptime_label, 2, 1)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.add_widget(stats_widget)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.clicked.connect(self.start_monitoring)
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏸️ Stop")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_metrics)
        controls_layout.addWidget(self.reset_btn)

        controls_layout.addStretch()

        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        self.add_widget(controls_widget)

    def setup_monitoring(self):
        """Setup monitoring timer"""
        self.start_time = time.time()
        self.monitoring_active = False

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.setInterval(1000)  # Update every second

    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        self.start_time = time.time()
        self.update_timer.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        self.update_timer.stop()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def reset_metrics(self):
        """Reset all metrics to zero"""
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "response_time": 0.0,
            "requests_per_second": 0.0,
        }
        self.update_display()

    def update_metrics(self):
        """Update performance metrics"""
        if not self.monitoring_active:
            return

        try:
            # Simulate metrics (in real implementation, use psutil)
            import random

            self.metrics["cpu_usage"] = random.uniform(10, 80)
            self.metrics["memory_usage"] = random.uniform(20, 60)
            self.metrics["response_time"] = random.uniform(50, 500)
            self.metrics["requests_per_second"] = random.uniform(10, 100)

            self.update_display()

        except Exception as e:
            print(f"Error updating metrics: {e}")

    def update_display(self):
        """Update the display with current metrics"""
        # Update progress bars
        self.cpu_bar.setValue(int(self.metrics["cpu_usage"]))
        self.cpu_label.setText(f"{self.metrics['cpu_usage']:.1f}%")

        self.memory_bar.setValue(int(self.metrics["memory_usage"]))
        self.memory_label.setText(f"{self.metrics['memory_usage']:.1f}%")

        # Update stats labels
        self.response_time_label.setText(f"{self.metrics['response_time']:.0f}ms")
        self.rps_label.setText(f"{self.metrics['requests_per_second']:.1f}")

        # Update uptime
        if self.monitoring_active:
            uptime = time.time() - self.start_time
            if uptime < 60:
                self.uptime_label.setText(f"{uptime:.0f}s")
            elif uptime < 3600:
                self.uptime_label.setText(f"{uptime / 60:.1f}m")
            else:
                self.uptime_label.setText(f"{uptime / 3600:.1f}h")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.metrics.copy()
