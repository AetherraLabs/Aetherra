#!/usr/bin/env python3
"""
🔴 AETHERRA OS LIVE ACTIVITY MONITOR
====================================
Real-time monitoring of Aetherra OS activity and performance.

Aligned to current endpoints:
- Hub Server (port 3001): /health, /status, /api/stats, /api/plugins
- Web Interface (port 8686): /api/system/status, /api/metrics/realtime
"""

import argparse
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests


HUB_BASE = "http://localhost:3001"
WEB_BASE = "http://localhost:8686"


def _fetch_json(url: str, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(url, timeout=timeout)
        if r.ok:
            return r.json()
        return None
    except requests.exceptions.RequestException:
        return None


def _tail_log(path: str, lines: int = 10) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            buf = f.readlines()
            return [ln.rstrip() for ln in buf[-lines:] if ln.strip()]
    except FileNotFoundError:
        return []


def render_once():
    print("🔴 AETHERRA OS LIVE ACTIVITY MONITOR")
    print("=" * 50)
    print("Monitoring real-time system activity…")
    print()

    # Hub server status (authoritative)
    health = _fetch_json(f"{HUB_BASE}/health")
    status = _fetch_json(f"{HUB_BASE}/status")
    stats = _fetch_json(f"{HUB_BASE}/api/stats")
    plugins = _fetch_json(f"{HUB_BASE}/api/plugins")

    if health or status:
        print("🟢 HUB: ONLINE")
        uptime = None
        if health and isinstance(health.get("uptime_seconds"), (int, float)):
            uptime = int(health.get("uptime_seconds", 0))
        elif status and isinstance(status.get("uptime_seconds"), (int, float)):
            uptime = int(status.get("uptime_seconds", 0))
        reqs = None
        if health:
            reqs = health.get("requests_served")
        if reqs is None and stats:
            reqs = stats.get("requests_served")
        plugin_count = 0
        if plugins and isinstance(plugins.get("plugins"), list):
            plugin_count = len(plugins.get("plugins", []))
        elif health and isinstance(health.get("plugins_registered"), int):
            plugin_count = health.get("plugins_registered", 0)
        print(f"   ⏱️ Uptime: {uptime or 0}s   •   📈 Requests: {reqs or 0}   •   🔌 Plugins: {plugin_count}")
    else:
        print("🔴 HUB: Not responding on localhost:3001")

    # Web interface (optional)
    web_status = _fetch_json(f"{WEB_BASE}/api/system/status")
    metrics = _fetch_json(f"{WEB_BASE}/api/metrics/realtime")
    if web_status or metrics:
        print("🟢 WEB INTERFACE: ACTIVE")
        if metrics:
            cpu = metrics.get("cpu_usage")
            mem = metrics.get("memory_usage")
            rt = metrics.get("response_time")
            extras = []
            if isinstance(cpu, (int, float)):
                extras.append(f"CPU {cpu}%")
            if isinstance(mem, (int, float)):
                extras.append(f"MEM {mem}%")
            if isinstance(rt, (int, float)):
                extras.append(f"RT {rt}ms")
            if extras:
                print("   " + "   •   ".join(extras))
    else:
        print("🟡 WEB INTERFACE: Not detected on localhost:8686 (optional)")

    # Recent log activity
    recent = _tail_log("aetherra_os.log", lines=10)
    print()
    print("📋 RECENT SYSTEM ACTIVITY:")
    print("-" * 30)
    if recent:
        for line in recent:
            print(f"   {line}")
    else:
        print("   (no recent log lines or log missing)")

    # Summary footer
    print()
    print("⚡ SYSTEM STATUS:")
    print("-" * 20)
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"🕐 Current Time: {current_time}")
    print("Components: Service Registry • Plugin Discovery • Memory • Hub • Web UI • Core Engine")
    print()
    print("=" * 50)


def monitor_aetherra_activity(watch_interval: int = 0):
    if watch_interval <= 0:
        render_once()
        return

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            render_once()
            time.sleep(watch_interval)
    except KeyboardInterrupt:
        print("\n� Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aetherra OS Live Monitor")
    parser.add_argument(
        "--watch",
        type=int,
        default=0,
        help="Refresh every N seconds (0 = one-shot)",
    )
    args = parser.parse_args()
    monitor_aetherra_activity(args.watch)
