#!/usr/bin/env python3
"""
Chat Stream Demo
- Minimal CLI to stream chat output from the Aetherra Hub developer AI API when enabled.
- Falls back to non-streaming /api/ai/ask if streaming is unavailable.

Usage:
  python demos/chat_stream_demo.py --prompt "Explain HMR in two sentences"

Env (optional):
  AETHERRA_BASE_URL           e.g., http://127.0.0.1:3001
  AETHERRA_WEB_HOST/PORT      defaults: localhost / 3001
  AETHERRA_HUB_HOST/PORT      fallback host/port
  AETHERRA_AI_API_TOKEN       bearer for X-Aetherra-Token
  AETHERRA_HUB_CONTROL_TOKEN  alternate token if AI token not set

Exit codes:
  0 success, 1 request error, 2 API unavailable/disabled
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Optional

try:
    import requests
except Exception:
    print("requests is required. Please install it in your environment.")
    sys.exit(2)


def resolve_base_url() -> str:
    env = os.environ.get("AETHERRA_BASE_URL")
    if env:
        return env.rstrip("/")
    host = (
        os.environ.get("AETHERRA_WEB_HOST")
        or os.environ.get("AETHERRA_HUB_HOST")
        or "127.0.0.1"
    )
    try:
        port = int(
            os.environ.get("AETHERRA_WEB_PORT")
            or os.environ.get("AETHERRA_HUB_PORT")
            or 3001
        )
    except Exception:
        port = 3001
    return f"http://{host}:{port}"


def get_headers() -> Dict[str, str]:
    token = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
        "AETHERRA_HUB_CONTROL_TOKEN"
    )
    return {"X-Aetherra-Token": token} if token else {}


def _print_awareness(aw: Optional[dict]):
    """Pretty-print awareness to stdout in a compact, UI-friendly format.

    Emits optional lines prefixed so consumers (like the PySide log pane)
    can show them directly without extra parsing.
    """
    if not isinstance(aw, dict):
        return
    cb = aw.get("confidence_breakdown")
    if isinstance(cb, dict) and cb:
        parts = []
        for k, v in cb.items():
            try:
                parts.append(f"{k}:{float(v):.2f}")
            except Exception:
                parts.append(f"{k}:{v}")
        print("[CONF] " + " | ".join(parts))
    ev = aw.get("evidence")
    if isinstance(ev, list) and ev:
        # Limit to top 3 for brevity
        for i, item in enumerate(ev[:3], start=1):
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("id") or "evidence"
            src = item.get("source") or item.get("path") or ""
            score = item.get("score")
            if score is not None:
                try:
                    score_str = f"{float(score):.2f}"
                except Exception:
                    score_str = str(score)
            else:
                score_str = ""
            line = f"[EVID {i}] {title}"
            if src:
                line += f" — {src}"
            if score_str:
                line += f" (score {score_str})"
            print(line)


def _print_persona(persona: Optional[object]):
    if persona is None:
        return
    # Accept string or dict with name/id
    if isinstance(persona, str):
        if persona.strip():
            print(f"[PERSONA] {persona.strip()}")
        return
    if isinstance(persona, dict):
        name = persona.get("name") or persona.get("id") or persona.get("persona")
        if name:
            print(f"[PERSONA] {name}")


def _print_model(model: Optional[str]):
    if isinstance(model, str) and model.strip():
        print(f"[MODEL] {model.strip()}")


def _print_suggestions(suggestions: Optional[object]):
    if not isinstance(suggestions, list):
        return
    for i, s in enumerate(suggestions[:5], start=1):
        text = None
        if isinstance(s, str):
            text = s
        elif isinstance(s, dict):
            text = s.get("text") or s.get("label") or s.get("title")
        if text:
            print(f"[SUG {i}] {str(text)}")


def _print_applied_changes(changes: Optional[object]):
    if not isinstance(changes, list):
        return
    for i, ch in enumerate(changes[:5], start=1):
        if isinstance(ch, dict):
            path = ch.get("path") or ch.get("file") or ch.get("target") or "change"
            desc = ch.get("summary") or ch.get("description") or ch.get("message") or ""
            if desc:
                print(f"[APPLIED {i}] {path} — {desc}")
            else:
                print(f"[APPLIED {i}] {path}")
        else:
            print(f"[APPLIED {i}] {str(ch)}")


def _print_usage(usage: Optional[object]):
    if not isinstance(usage, dict):
        return
    try:
        pt = usage.get("prompt_tokens")
        ct = usage.get("completion_tokens")
        tt = usage.get("total_tokens")
        lm = usage.get("latency_ms") or usage.get("latency")
        parts = []
        if pt is not None:
            parts.append(f"prompt={pt}")
        if ct is not None:
            parts.append(f"completion={ct}")
        if tt is not None:
            parts.append(f"total={tt}")
        if lm is not None:
            parts.append(f"latency_ms={lm}")
        if parts:
            print("[USAGE] " + " | ".join(parts))
    except Exception:
        pass


def try_stream(base: str, prompt: str) -> Optional[int]:
    url = base.rstrip("/") + "/api/ai/stream"
    payload = {"message": prompt}
    headers = get_headers()
    try:
        with requests.post(
            url, json=payload, headers=headers, stream=True, timeout=10
        ) as r:
            if r.status_code == 501:
                print(
                    "[INFO] Streaming API disabled (501). Falling back to /api/ai/ask."
                )
                return None
            if r.status_code == 403:
                print("[ERR] Forbidden (403). If required, set AETHERRA_AI_API_TOKEN.")
                return 1
            r.raise_for_status()
            print(f"[STREAM] connected: {url}")
            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                line = str(raw)
                if line.startswith(":"):
                    # comment/keepalive
                    continue
                # Expect SSE: event: <name> / data: <json>
                if line.startswith("event:"):
                    evt = line.split(":", 1)[1].strip()
                    print(f"[SSE] event={evt}")
                    continue
                if line.startswith("data:"):
                    data = line.split(":", 1)[1].strip()
                    print(f"[SSE] data={data}")
                    # Try to parse the envelope and surface awareness when final arrives
                    try:
                        env = json.loads(data)
                        # Envelope shape: { id, trace_id, ts, type, data, ... }
                        if not isinstance(env, dict):
                            pass
                        else:
                            etype = env.get("type")
                            edata = env.get("data")
                            if etype == "delta" and isinstance(edata, dict):
                                chunk = (
                                    edata.get("delta")
                                    or edata.get("chunk")
                                    or edata.get("text")
                                    or edata.get("content")
                                )
                                if isinstance(chunk, str) and chunk:
                                    print(f"[CHUNK] {chunk}")
                            if etype == "final" and isinstance(edata, dict):
                                result = edata.get("result")
                                if isinstance(result, dict):
                                    # Model/persona
                                    _print_model(result.get("model"))
                                    _print_persona(result.get("persona"))
                                    # Awareness
                                    aw = result.get("awareness")
                                    _print_awareness(
                                        aw if isinstance(aw, dict) else None
                                    )
                                    # Suggestions and applied changes
                                    _print_suggestions(result.get("suggestions"))
                                    _print_applied_changes(
                                        result.get("applied_changes")
                                    )
                                    # Usage metadata
                                    usage = result.get("usage") or env.get("usage")
                                    _print_usage(usage)
                    except Exception:
                        pass
                    # If final, we can decide to stop; let server close normally
                    continue
                # Fallback: print raw
                print(f"[SSE] {line}")
            print("[DONE] stream closed")
            return 0
    except requests.HTTPError as he:
        code = getattr(he.response, "status_code", None)
        if code in (404, 405):
            print("[INFO] Streaming endpoint not found. Falling back to /api/ai/ask.")
            return None
        print(f"[ERR] streaming HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] streaming failed: {e}")
        return 1


def try_ask(base: str, prompt: str) -> int:
    url = base.rstrip("/") + "/api/ai/ask"
    payload = {"message": prompt}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 501:
            print(
                "[INFO] AI API disabled (501). Enable AETHERRA_AI_API_ENABLED=1 on the Hub and retry."
            )
            return 2
        if r.status_code == 403:
            print("[ERR] Forbidden (403). If required, set AETHERRA_AI_API_TOKEN.")
            return 1
        r.raise_for_status()
        data = r.json()
        if (
            isinstance(data, dict)
            and data.get("ok")
            and isinstance(data.get("result"), dict)
        ):
            out = data["result"].get("response") or data["result"].get("text")
            if out:
                print("[RESPONSE] " + str(out))
            # Awareness (non-stream path)
            try:
                aw = data["result"].get("awareness")
                if isinstance(aw, dict):
                    _print_awareness(aw)
                # Persona / model
                _print_model(data["result"].get("model"))
                _print_persona(data["result"].get("persona"))
                # Suggestions / applied changes
                _print_suggestions(data["result"].get("suggestions"))
                _print_applied_changes(data["result"].get("applied_changes"))
                # Usage metadata
                usage = data["result"].get("usage") or data.get("usage")
                _print_usage(usage)
            except Exception:
                pass
            else:
                print("[JSON] " + json.dumps(data))
            return 0
        print("[JSON] " + json.dumps(data))
        return 0 if isinstance(data, dict) and data.get("ok") else 1
    except requests.HTTPError as he:
        print(f"[ERR] ask HTTP error: {he}")
        return 1
    except Exception as e:
        print(f"[ERR] ask failed: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat stream demo")
    parser.add_argument("--prompt", required=True, help="message to send")
    args = parser.parse_args()

    base = resolve_base_url()
    print(f"[BASE] {base}")

    rc = try_stream(base, args.prompt)
    if rc is None:
        return try_ask(base, args.prompt)
    return int(rc)


if __name__ == "__main__":
    sys.exit(main())
