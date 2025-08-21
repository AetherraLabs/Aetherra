#!/usr/bin/env python3
"""
Self-Improvement Demo
Runs the SelfImprovementEngine for a short burst, records metrics,
prints proposals and trends, then shuts down cleanly.
"""

import asyncio
import json
import random
from pathlib import Path

from Aetherra.aetherra_core.engine.self_improvement_engine import SelfImprovementEngine


async def main():
    db_path = Path("demos/self_improvement_demo.db")
    engine = SelfImprovementEngine(db_path=str(db_path))

    await engine.start_improvement_cycle()

    # Simulate some metrics over ~2 seconds
    for _ in range(25):
        engine.record_performance_metric(
            "response_time", 100 + random.uniform(-20, 60), "ms"
        )
        engine.record_performance_metric(
            "cpu_usage", 55 + random.uniform(-5, 40), "percent"
        )
        engine.record_performance_metric(
            "error_rate", max(0.0, random.uniform(-0.01, 0.05)), "ratio"
        )
        await asyncio.sleep(0.05)

    # Let analysis run at least once
    await asyncio.sleep(1.0)

    print("\n=== Self-Improvement Status ===")
    print(json.dumps(engine.get_improvement_status(), indent=2))

    print("\n=== Metric Trends ===")
    print(json.dumps(engine.get_metric_trends(), indent=2, default=str))

    await engine.stop_improvement_cycle()
    print("\nDemo complete. DB at:", db_path)


if __name__ == "__main__":
    asyncio.run(main())
