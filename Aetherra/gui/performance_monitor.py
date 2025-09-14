#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
📊 Performance Monitoring System
===============================

Monitors resource usage, UI responsiveness, and enforces performance budgets.
Provides automatic cleanup and watchdogs for the Lyrixa GUI.

Key Features:
- Memory and CPU usage tracking
- UI responsiveness watchdog
- Performance budgets for plugins and core components
- Automatic cleanup of resource leaks
- Event-driven reporting and alerts
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

import psutil
from PySide6.QtCore import QObject, QTimer, Signal, Slot

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""

    timestamp: float
    memory_mb: float
    cpu_percent: float
    widget_count: int
    plugin_count: int
    ui_responsive: bool
    alerts: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor(QObject):
    """
    Monitors performance and enforces budgets for Lyrixa GUI.
    Emits alerts and triggers cleanup when thresholds are exceeded.
    """

    # Signals
    metrics_updated = Signal(object)  # PerformanceMetrics
    alert_triggered = Signal(str)  # alert message
    cleanup_triggered = Signal(str)  # reason

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        self.memory_budget_mb = 1024
        self.cpu_budget_percent = 50
        self.widget_budget = 2000
        self.plugin_budget = 50
        self.ui_responsiveness_budget_ms = 500

        self._metrics_history: list[PerformanceMetrics] = []
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._collect_metrics)
        self._monitor_timer.start(3000)  # Every 3 seconds

        logger.info("PerformanceMonitor initialized")

    @Slot()
    def _collect_metrics(self) -> None:
        """Collect and analyze performance metrics."""
        try:
            timestamp = time.time()
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)
            cpu_percent = process.cpu_percent(interval=0.1)

            # Widget and plugin counts (stub, integrate with GUI)
            widget_count = self._get_widget_count()
            plugin_count = self._get_plugin_count()

            # UI responsiveness (stub)
            ui_responsive = self._check_ui_responsiveness()

            alerts = []
            if memory_mb > self.memory_budget_mb:
                alerts.append(
                    f"Memory usage exceeded: {memory_mb:.1f} MB > {self.memory_budget_mb} MB"
                )
            if cpu_percent > self.cpu_budget_percent:
                alerts.append(
                    f"CPU usage exceeded: {cpu_percent:.1f}% > {self.cpu_budget_percent}%"
                )
            if widget_count > self.widget_budget:
                alerts.append(
                    f"Widget count exceeded: {widget_count} > {self.widget_budget}"
                )
            if plugin_count > self.plugin_budget:
                alerts.append(
                    f"Plugin count exceeded: {plugin_count} > {self.plugin_budget}"
                )
            if not ui_responsive:
                alerts.append("UI responsiveness degraded")

            metrics = PerformanceMetrics(
                timestamp=timestamp,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                widget_count=widget_count,
                plugin_count=plugin_count,
                ui_responsive=ui_responsive,
                alerts=alerts,
            )
            self._metrics_history.append(metrics)
            self.metrics_updated.emit(metrics)

            for alert in alerts:
                self.alert_triggered.emit(alert)
                logger.warning(f"Performance alert: {alert}")
                if "exceeded" in alert or "degraded" in alert:
                    self._trigger_cleanup(alert)
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")

    def _get_widget_count(self) -> int:
        """Stub: Integrate with QApplication for widget count."""
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                return len(app.allWidgets())
        except Exception:
            logging.exception("Exception occurred in _get_widget_count")
        return 0

    def _get_plugin_count(self) -> int:
        """Stub: Integrate with plugin manager for count."""
        # Replace with actual plugin manager integration
        return 0

    def _check_ui_responsiveness(self) -> bool:
        """Stub: Check UI responsiveness."""
        # Replace with actual responsiveness check
        return True

    def _trigger_cleanup(self, reason: str) -> None:
        """Trigger automatic cleanup when budgets are exceeded."""
        self.cleanup_triggered.emit(reason)
        logger.info(f"Triggered cleanup: {reason}")

    def get_metrics_history(self) -> list[PerformanceMetrics]:
        """Get history of collected metrics."""
        return self._metrics_history.copy()

    def set_budgets(
        self,
        memory_mb: int | None = None,
        cpu_percent: int | None = None,
        widget_count: int | None = None,
        plugin_count: int | None = None,
        ui_responsiveness_ms: int | None = None,
    ) -> None:
        """Set performance budgets."""
        if memory_mb:
            self.memory_budget_mb = memory_mb
        if cpu_percent:
            self.cpu_budget_percent = cpu_percent
        if widget_count:
            self.widget_budget = widget_count
        if plugin_count:
            self.plugin_budget = plugin_count
        if ui_responsiveness_ms:
            self.ui_responsiveness_budget_ms = ui_responsiveness_ms

    logger.info("Updated performance budgets")
