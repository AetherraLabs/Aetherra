# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for legacy ``memory.qfac_dashboard`` imports."""

from __future__ import annotations

import asyncio

from flask import Flask, jsonify

from Aetherra.aetherra_core.memory.qfac_dashboard import QFACDashboard


class _LegacyQFACAnalyzer:
    async def get_compression_performance(self) -> dict:
        return {
            "overall_health": 1.0,
            "performance_by_type": {},
            "performance_issues": [],
            "optimization_suggestions": [],
        }


class _LegacyQFACMemorySystem:
    async def get_system_status(self) -> dict:
        return {
            "size_statistics": {
                "overall_compression_ratio": 1.0,
                "space_saved_percentage": 0.0,
            },
            "system_health": 1.0,
            "node_statistics": {"total_nodes": 0, "compressed_nodes": 0},
        }


_dashboard = QFACDashboard(
    analyzer=_LegacyQFACAnalyzer(),
    memory_system=_LegacyQFACMemorySystem(),
)
app = Flask(__name__)


@app.get("/qfac/metrics")
def qfac_metrics():
    return jsonify(asyncio.run(_dashboard.get_dashboard_summary()))

__all__ = ["app"]
