#!/usr/bin/env python3
"""
Aetherra Demos Runner
- chat_lyrixa_bridge: POST /api/lyrixa/chat
- kernel_boot_status: GET /api/stats
- site_status_dashboard: GET /api/site_status
- quantum_status: GET /api/quantum/status
- quantum_run: POST /api/quantum/run
 - qhash: compute SimHash for a text and show hex + bit count

Env:
- AETHERRA_WEB_HOST (default: localhost)
- AETHERRA_WEB_PORT (default: 3001)
"""

import argparse
import json
import os
import sys
from typing import Any, Dict

try:
    import requests
except Exception:
    print("requests is required. Please install it in your environment.")
    sys.exit(2)

HOST = os.environ.get("AETHERRA_WEB_HOST", "localhost").strip() or "localhost"
PORT = int(os.environ.get("AETHERRA_WEB_PORT", "3001") or 3001)
BASE = f"http://{HOST}:{PORT}"


def _get(url: str) -> Dict[str, Any]:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def _post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


# Demo: Lyrixa chat bridge


def demo_chat_lyrixa_bridge(args: argparse.Namespace) -> int:
    message = args.message or "Who are you?"
    allow_edits = bool(args.allow_edits)
    payload = {"message": message, "allow_edits": allow_edits}
    if args.edit_root:
        payload["edit_root"] = args.edit_root
    try:
        data = _post(f"{BASE}/api/lyrixa/chat", payload)
    except Exception as e:
        print(f"[ERR] chat request failed: {e}")
        return 1
    # Print compact result
    text = data.get("text") or data.get("response") or data
    print("\n=== Lyrixa Chat Bridge ===")
    if isinstance(text, str):
        print(text)
    else:
        print(json.dumps(data, indent=2))
    # Optional extras
    if isinstance(data, dict):
        sugg = data.get("suggestions")
        if isinstance(sugg, list) and sugg:
            print("\nSuggestions:")
            for s in sugg[:5]:
                print(f" - {s}")
        applied = data.get("applied_changes")
        if isinstance(applied, list) and applied:
            print("\nApplied changes:")
            for ch in applied[:5]:
                print(f" - {ch}")
    return 0


# Demo: Kernel boot/status via hub stats


def demo_kernel_boot_status(args: argparse.Namespace) -> int:
    try:
        stats = _get(f"{BASE}/api/stats")
    except Exception as e:
        print(f"[ERR] failed to fetch stats: {e}")
        return 1
    print("\n=== Hub Stats ===")
    print(f"requests_served: {stats.get('requests_served')}")
    print(f"plugins_registered: {stats.get('plugins_registered')}")
    # Lyrixa registration summary
    ly = stats.get("lyrixa_chat") or {}
    if isinstance(ly, dict):
        print("lyrixa_chat:")
        print(f"  registered: {ly.get('registered')}")
        if ly.get("status"):
            print(f"  status: {ly.get('status')}")
        if ly.get("last_heartbeat"):
            print(f"  last_heartbeat: {ly.get('last_heartbeat')}")
    return 0


# Demo: Site status compact dashboard


def demo_site_status_dashboard(args: argparse.Namespace) -> int:
    try:
        d = _get(f"{BASE}/api/site_status")
    except Exception as e:
        print(f"[ERR] failed to fetch site_status: {e}")
        return 1
    print("\n=== Site Status ===")
    hub = d.get("hub", {})
    kern = d.get("kernel", {})
    plugins = d.get("plugins", {})
    print(f"hub.ts: {hub.get('ts')}  requests_served: {hub.get('requests_served')}")
    print(
        f"kernel.running: {kern.get('running')}  uptime_seconds: {kern.get('uptime_seconds')}"
    )
    q = kern.get("queue_sizes", {}) if isinstance(kern, dict) else {}
    print("queue_sizes:")
    print(
        f"  high: {q.get('high_priority')}  normal: {q.get('normal_priority')}  background: {q.get('background')}"
    )
    print(f"plugins.total: {plugins.get('total')}")
    return 0


# Demo: Quantum endpoints


def demo_quantum_status(args: argparse.Namespace) -> int:
    try:
        st = _get(f"{BASE}/api/quantum/status")
    except requests.HTTPError as he:  # type: ignore[name-defined]
        code = getattr(he.response, "status_code", None)
        if code in (404, 405):
            print("\n[INFO] Quantum endpoints not available on the running Hub.")
            print(
                "       Restart the Aetherra OS/Hub to load the new routes, then retry."
            )
            try:
                _get(f"{BASE}/api/stats")
                print(
                    "       Hub is online; just needs a restart to pick up endpoints."
                )
            except Exception:
                print("       Hub may be offline; start the OS/Hub and retry.")
            return 2
        print(f"[ERR] quantum status HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] failed to fetch quantum status: {e}")
        return 1
    print("\n=== Quantum Status ===")
    if isinstance(st, dict):
        mode = st.get("mode")
        provider = st.get("provider")
        print(f"mode: {mode}  provider: {provider}")
        print(
            f"jobs_total: {st.get('jobs_total')}  shots_total: {st.get('shots_total')}"
        )
        print(
            f"queue_current: {st.get('queue_current')}  cost_usd: {st.get('cost_usd')}  error_rate: {st.get('error_rate')}"
        )
    else:
        print(st)
    return 0


def demo_quantum_run(args: argparse.Namespace) -> int:
    payload = {
        "shots": int(args.shots or 100),
    }
    if args.seed is not None:
        try:
            payload["seed"] = int(args.seed)
        except Exception:
            pass
    try:
        res = _post(f"{BASE}/api/quantum/run", payload)
    except requests.HTTPError as he:  # type: ignore[name-defined]
        code = getattr(he.response, "status_code", None)
        if code in (404, 405):
            print("\n[INFO] Quantum run endpoint not available on the running Hub.")
            print(
                "       Restart the Aetherra OS/Hub to load the new routes, then retry."
            )
            return 2
        print(f"[ERR] quantum run HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] quantum run failed: {e}")
        return 1
    print("\n=== Quantum Run ===")
    if isinstance(res, dict):
        print(
            f"job_id: {res.get('job_id')}  ok: {res.get('ok')}  shots: {res.get('shots')} seed: {res.get('seed')}"
        )
        counts = (
            (res.get("result") or {}).get("counts")
            if isinstance(res.get("result"), dict)
            else None
        )
        if isinstance(counts, dict):
            total = sum(int(v) for v in counts.values())
            print(f"counts keys: {list(counts.keys())}  total: {total}")
        else:
            print(res)
    else:
        print(res)
    return 0


def demo_qhash(args: argparse.Namespace) -> int:
    try:
        from Aetherra.aetherra_core.memory.quantum.qhash import simhash_text, to_hex
    except Exception as e:
        print(f"[ERR] qhash module not available: {e}")
        return 1
    bits = int(args.bits or 64)
    h = simhash_text(args.text or "", bits=bits, seed=args.seed)
    hx = to_hex(h, bits=bits)
    print("\n=== QHash (SimHash) ===")
    print(f"bits: {bits}")
    print(f"hash: {hx}")
    print(f"set_bits: {int(h).bit_count()}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Aetherra demo runner")
    sub = parser.add_subparsers(dest="demo", required=True)

    p1 = sub.add_parser("chat_lyrixa_bridge", help="POST /api/lyrixa/chat")
    p1.add_argument("--message", "-m", help="message to send")
    p1.add_argument("--allow-edits", action="store_true")
    p1.add_argument("--edit-root", help="edit root id or path")
    p1.set_defaults(func=demo_chat_lyrixa_bridge)

    p2 = sub.add_parser("kernel_boot_status", help="GET /api/stats")
    p2.set_defaults(func=demo_kernel_boot_status)

    p3 = sub.add_parser("site_status_dashboard", help="GET /api/site_status")
    p3.set_defaults(func=demo_site_status_dashboard)

    p4 = sub.add_parser("quantum_status", help="GET /api/quantum/status")
    p4.set_defaults(func=demo_quantum_status)

    p5 = sub.add_parser("quantum_run", help="POST /api/quantum/run")
    p5.add_argument("--shots", type=int, default=100)
    p5.add_argument("--seed", type=int)
    p5.set_defaults(func=demo_quantum_run)

    p6 = sub.add_parser("qhash", help="Compute SimHash for a given text")
    p6.add_argument("text")
    p6.add_argument("--bits", type=int, default=64)
    p6.add_argument("--seed", type=int)
    p6.set_defaults(func=demo_qhash)

    args = parser.parse_args()
    rc = args.func(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
