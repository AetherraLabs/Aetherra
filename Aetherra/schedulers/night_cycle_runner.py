# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Night Cycle Scheduler — Phase 4
================================

Orchestrates offline reflective learning during idle periods.
Runs dream cycle and memory consolidation.

Design:
- Invoked via systemd timer (preferred) or internal idle detection
- Coordinates DreamCycle and Consolidator
- Logs results to structured output
- Safe: skips run if system is under load
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


def run(
    consciousness_core: Any,
    memory_engine: Any,
    skip_if_load_above: float = 0.7,
) -> Dict[str, Any]:
    """Execute night cycle (dream + consolidation).

    Args:
        consciousness_core: ConsciousnessCore instance
        memory_engine: MemoryEngine instance
        skip_if_load_above: Skip if system load (normalized) exceeds this (default: 0.7)

    Returns:
        Dict with cycle results (dream stats, consolidation stats, errors)
    """
    start_ts = time.time()

    logger.info("Night cycle starting...")

    # Safety: check system load
    if _get_system_load() > skip_if_load_above:
        logger.warning("System load too high, skipping night cycle")
        return {
            "status": "skipped",
            "reason": "system_load_high",
            "duration_seconds": 0,
        }

    results = {
        "status": "running",
        "start_ts": start_ts,
        "dream": {},
        "consolidation": {},
        "errors": [],
    }

    # Run dream cycle
    try:
        if not hasattr(consciousness_core, "dream_cycle"):
            logger.warning("ConsciousnessCore has no dream_cycle attribute")
            results["errors"].append("dream_cycle_missing")
        else:
            dream_results = consciousness_core.dream_cycle.run(
                consciousness_core.qualia_learner
            )
            results["dream"] = dream_results
            logger.info(
                f"Dream cycle completed: {dream_results.get('snapshots_analyzed', 0)} snapshots analyzed"
            )

    except Exception as e:
        logger.error(f"Dream cycle failed: {e}", exc_info=True)
        results["errors"].append(f"dream_cycle_error: {e}")

    # Run memory consolidation
    try:
        if not hasattr(consciousness_core, "consolidator"):
            logger.warning("ConsciousnessCore has no consolidator attribute")
            results["errors"].append("consolidator_missing")
        else:
            consolidation_results = consciousness_core.consolidator.consolidate()
            results["consolidation"] = consolidation_results
            logger.info(
                f"Consolidation completed: {consolidation_results.get('pruned', 0)} pruned, "
                f"{consolidation_results.get('promoted', 0)} promoted"
            )

    except Exception as e:
        logger.error(f"Consolidation failed: {e}", exc_info=True)
        results["errors"].append(f"consolidation_error: {e}")

    # Finalize
    duration = time.time() - start_ts
    results["duration_seconds"] = duration
    results["status"] = "completed" if not results["errors"] else "completed_with_errors"

    logger.info(f"Night cycle finished in {duration:.2f}s")

    return results


def _get_system_load() -> float:
    """Get normalized system load (0.0 = idle, 1.0 = saturated).

    Returns:
        Normalized load (0.0-1.0+)
    """
    try:
        import os

        # Get 1-minute load average
        load = os.getloadavg()[0]

        # Normalize by CPU count
        cpu_count = os.cpu_count() or 1
        normalized = load / cpu_count

        return normalized

    except Exception:
        # Fallback: assume low load
        return 0.0


def main() -> int:
    """CLI entry point for manual night cycle invocation.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        # Import consciousness system
        from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
        from Aetherra.memory.memory_engine import MemoryEngine

        # Initialize components
        logger.info("Initializing consciousness core...")
        memory_engine = MemoryEngine()
        core = ConsciousnessCore(memory_engine=memory_engine)

        # Run night cycle
        results = run(core, memory_engine)

        # Print results
        print("\nNight Cycle Results:")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f}s")

        if results.get("dream"):
            print("\nDream Cycle:")
            dream = results["dream"]
            print(f"  Snapshots analyzed: {dream.get('snapshots_analyzed', 0)}")
            print(f"  Adjustments made: {dream.get('adjustments', {})}")
            if dream.get("narrative"):
                print(f"\n  Narrative:\n{dream['narrative']}\n")

        if results.get("consolidation"):
            print("\nMemory Consolidation:")
            cons = results["consolidation"]
            print(f"  Entries pruned: {cons.get('pruned', 0)}")
            print(f"  Entries promoted: {cons.get('promoted', 0)}")
            print(f"  Errors: {cons.get('errors', 0)}")

        if results.get("errors"):
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")

        return 0 if results["status"] == "completed" else 1

    except Exception as e:
        logger.error(f"Night cycle failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
