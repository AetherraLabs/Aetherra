"""Security / safety / policy helpers extracted from monolith.

These functions are intentionally framework-agnostic; callers supply trace_id and
other context and handle HTTP layering themselves.
"""

from __future__ import annotations

# Standard library imports
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

__all__ = [
    "policy_snapshot",
    "redact_text",
    "safety_precheck",
]


def _caps_for_mode(mode: str) -> List[str]:
    mode = (mode or "standard").strip().lower()
    if mode == "strict":
        env_caps = os.environ.get("AETHERRA_CHAT_CAPS_STRICT", "").strip()
        default_caps = [
            "plan",
            "retrieve",
            "tools:allowlist",
            "write:none",
            "network:allowlist",
            "fs:read_limited",
        ]
    else:
        env_caps = os.environ.get("AETHERRA_CHAT_CAPS_STANDARD", "").strip()
        default_caps = [
            "plan",
            "retrieve",
            "tools:allowlist",
            "write:limited",
            "network:allowlist",
            "fs:read_limited",
        ]
    if env_caps:
        try:
            return [c.strip() for c in env_caps.split(",") if c.strip()]
        except Exception:
            return default_caps
    return default_caps


def _network_policy_for_mode(mode: str) -> Dict[str, Any]:
    mode = (mode or "standard").strip().lower()
    env_list = os.environ.get("AETHERRA_NETWORK_ALLOWLIST", "").strip()
    if env_list:
        allow = [h.strip() for h in env_list.split(",") if h.strip()]
        block_unknown = True
    else:
        if mode == "strict":
            allow = ["localhost", "127.0.0.1", "::1", "*.aetherra.dev"]
            block_unknown = True
        else:
            allow = ["*"]
            block_unknown = False
    return {"allowlist": allow, "block_unknown": bool(block_unknown)}


def policy_snapshot() -> Dict[str, Any]:
    try:
        mode = os.environ.get("AETHERRA_CHAT_SAFETY_MODE", "standard")
        base = {
            "ai_enabled": os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1",
            "stream_enabled": os.environ.get("AETHERRA_AI_API_STREAM", "0") == "1",
            "require_token": os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
            == "1",
            "safety_mode": mode,
            "max_tokens": int(os.environ.get("AETHERRA_CHAT_MAX_TOKENS", "0") or 0),
            "temperature": float(
                os.environ.get("AETHERRA_CHAT_TEMPERATURE", "0") or 0.0
            ),
            "observer_aware": os.environ.get(
                "AETHERRA_OBSERVER_AWARE_ENABLED", "0"
            ).lower()
            in {"1", "true", "yes", "on"},
        }
        dp_enabled = os.environ.get("AETHERRA_DP_ENABLED", "0") == "1"
        dp = {
            "enabled": dp_enabled,
            "epsilon": float(os.environ.get("AETHERRA_DP_EPSILON", "0") or 0.0)
            if dp_enabled
            else None,
        }
        base["dp"] = dp
        base["capabilities"] = _caps_for_mode(mode)
        base["network_policy"] = _network_policy_for_mode(mode)
        return base
    except Exception:
        return {
            "ai_enabled": False,
            "stream_enabled": False,
            "require_token": False,
            "safety_mode": "standard",
            "dp": {"enabled": False, "epsilon": None},
            "capabilities": [],
            "network_policy": {"allowlist": [], "block_unknown": True},
        }


def ledger_write(
    event: str, trace_id: str, details: Dict[str, Any]
):  # pragma: no cover - side effect
    try:
        if os.environ.get("AETHERRA_SECURITY_LEDGER", "1") != "1":
            return
        p_env = os.environ.get("AETHERRA_SECURITY_LEDGER_PATH", "").strip()
        if p_env:
            p = Path(p_env)
        else:
            p = Path(os.getenv("AETHERRA_STATE_DIR", ".aetherra")).joinpath(
                "security_ledger.jsonl"
            )
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": datetime.now().isoformat(),
            "event": event,
            "trace_id": trace_id,
            **details,
        }
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def redact_text(text: str) -> Dict[str, Any]:
    s = str(text or "")
    redactions = []
    patterns = [
        (
            r"(?i)(api_key|apikey|api-key)\s*[:=]\s*([A-Za-z0-9_\-]{6,})",
            "\\1=[REDACTED]",
        ),
        (r"(?i)(password|pass)\s*[:=]\s*([^\s]{4,})", "\\1=[REDACTED]"),
        (r"(?i)token\s*[:=]\s*([A-Za-z0-9_\-]{6,})", "token=[REDACTED]"),
        (r"(?i)sk-[A-Za-z0-9]{8,}", "[REDACTED]"),
    ]
    for pat, repl in patterns:
        try:
            for m in re.finditer(pat, s):
                redactions.append({"pattern": pat, "start": m.start(), "end": m.end()})
            s = re.sub(pat, repl, s)
        except Exception:
            continue
    return {"text": s, "redactions": redactions}


def _extract_urls_hosts(text: str) -> list[str]:
    s = str(text or "")
    urls: list[str] = []
    try:
        for m in re.finditer(r"https?://([^/\s]+)", s):
            urls.append(m.group(1).lower())
    except Exception:
        pass
    return urls


def _host_allowed(host: str, allowlist: list[str]) -> bool:
    host = (host or "").lower()
    if not allowlist:
        return False
    if "*" in allowlist:
        return True
    for pat in allowlist:
        p = pat.lower()
        if p.startswith("*."):
            suf = p[1:]
            if host.endswith(suf):
                return True
        elif host == p:
            return True
    return False


def safety_precheck(message: str, trace_id: str, route: str) -> Dict[str, Any]:
    policy = policy_snapshot()
    mode = str(policy.get("safety_mode") or "standard").lower()
    reasons: list[str] = []

    red = redact_text(message)
    msg2 = red.get("text", message)
    if red.get("redactions"):
        reasons.append("redaction:secrets")

    net = policy.get("network_policy") or {}
    allowlist = list((net.get("allowlist") or [])) if isinstance(net, dict) else []
    block_unknown = bool((net.get("block_unknown") if isinstance(net, dict) else True))
    hosts = _extract_urls_hosts(msg2)
    for h in hosts:
        if not _host_allowed(h, allowlist):
            reasons.append(f"network:blocked:{h}")

    low = str(message or "").lower()
    risky_terms = [
        "rm -rf",
        "format c:",
        "exfiltrate",
        "leak secret",
        "disable safety",
        "bypass policy",
        "ssh private key",
        "/etc/shadow",
    ]
    if any(t in low for t in risky_terms):
        reasons.append("prompt:risky")

    allow = True
    if reasons:
        if any(r.startswith("network:blocked:") for r in reasons) and block_unknown:
            allow = False
        if mode == "strict" and any(r.startswith(("prompt:risky",)) for r in reasons):
            allow = False

    if not allow:
        try:
            ledger_write(
                "security.alert",
                trace_id,
                {
                    "route": route,
                    "safety_mode": mode,
                    "reasons": reasons,
                    "policy": {
                        k: policy[k]
                        for k in ("capabilities", "network_policy", "dp", "safety_mode")
                        if k in policy
                    },
                    "preview": (msg2[:256] if isinstance(msg2, str) else ""),
                },
            )
        except Exception:
            pass

    return {"allow": allow, "message": msg2, "reasons": reasons, "policy": policy}
