"""/metrics Prometheus export (initial slimmed slice).

This is a first-step extraction. It currently emits only chat subset counters.
Additional kernel/orchestrator/HMR/memory metrics will migrate here iteratively.
"""

from __future__ import annotations

from flask import Blueprint, Response

from ..services import metrics_accum

bp = Blueprint("metrics", __name__)


@bp.get("/metrics")
def metrics_export():
    lines = metrics_accum.build_all_metrics_lines()
    body = metrics_accum.export_prometheus(lines)
    return Response(body, mimetype="text/plain; version=0.0.4; charset=utf-8")
