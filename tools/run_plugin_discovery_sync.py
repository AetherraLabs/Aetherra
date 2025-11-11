#!/usr/bin/env python3
import asyncio
import os
import socket
import sys
from urllib.parse import urlparse

from aetherra_plugin_discovery import AetherraPluginDiscovery


def _reachable(url: str) -> bool:
    """Fast reachability check using raw socket connect (avoids extra deps)."""
    try:
        if not url:
            return False
        p = urlparse(url)
        host = p.hostname or "127.0.0.1"
        port = p.port or 3001
        with socket.create_connection((host, port), timeout=0.75):
            return True
    except Exception:
        return False


def _scan_for_hub(start: int = 3001, end: int = 3060) -> str | None:
    """Scan a small port range for a responding Hub /api/ping endpoint."""
    import http.client

    for port in range(start, end + 1):
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=0.75)
            conn.request("GET", "/api/ping")
            resp = conn.getresponse()
            if resp.status == 200:
                conn.close()
                return f"http://localhost:{port}"
        except Exception:
            continue
    return None


def _from_runtime_file() -> str | None:
    for fname in ("hub_runtime_url.txt", "hub_port.txt"):
        try:
            if os.path.exists(fname):
                with open(fname, encoding="utf-8") as f:
                    raw = f.read().strip()
                    if raw:
                        # Normalize if only a port number present
                        if raw.isdigit():
                            return f"http://localhost:{raw}"
                        return raw
        except Exception:
            continue
    return None


def resolve_hub_url() -> str:
    # 0. Explicit override for this run
    force = os.environ.get("AETHERRA_FORCE_HUB_URL", "").strip()
    if force:
        return force
    # 1. Environment variable
    env_url = os.environ.get("AETHERRA_HUB_URL", "").strip()
    if env_url and _reachable(env_url):
        return env_url
    # 2. Runtime file written by launcher
    file_url = _from_runtime_file()
    if file_url and _reachable(file_url):
        return file_url
    # 3. Scan common ports
    scan_url = _scan_for_hub()
    if scan_url:
        return scan_url
    # 4. Fallback legacy defaults
    return "http://127.0.0.1:3012"


async def main():
    # Signing defaults
    os.environ.setdefault("AETHERRA_SIGN_PLUGINS", "1")
    os.environ.setdefault("AETHERRA_SIGNING_STRICT", "1")
    # Dev override: allow unsigned if hub can't verify signatures yet
    os.environ.setdefault("AETHERRA_ALLOW_UNSIGNED_DEV", "1")
    hub_url = resolve_hub_url()
    os.environ["AETHERRA_HUB_URL"] = hub_url
    print(f"[Runner] Target Hub resolved to: {hub_url}")
    discovery = AetherraPluginDiscovery()
    count = await discovery.sync_all_with_hub()
    print(f"[Runner] Registered {count} plugins against Hub {hub_url}")
    summary = discovery.get_plugin_summary()
    print(
        f"[Runner] Summary: {summary['total_plugins']} discovered -> {count} registered"
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Runner] Interrupted", file=sys.stderr)
