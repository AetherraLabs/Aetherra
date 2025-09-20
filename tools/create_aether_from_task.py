#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
One-click creator: generate a .aether script from a short task description.
Usage: python tools/create_aether_from_task.py "Build a memory smoke test"

Creates a file under scripts/ with a timestamped name and a standard template
including meta, policy with retries/timeouts, and a basic workflow scaffold.

Custom templates:
- Set AETHERRA_TEMPLATE_DIR to a directory containing a template file.
- The generator will look for (in order):
    - template.aether
    - default.aether
    and apply simple Python .format replacements with keys: created, task, slug, requires.
- If formatting fails or no file exists, the built-in template is used.

Env:
- AETHERRA_TEMPLATE_DIR: optional path to custom templates
- AETHERRA_REQUIRE_STRICT: set to 1 to include strict require directives
"""

from __future__ import annotations

# Standard library imports
import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_TEMPLATE = """
# @meta: {"created": "{created}", "author": "Lyrixa Code Studio", "task": "{task}"}
# @signature: <optional-signature>

# Deterministic test profile recommended for CI
policy profile="test" max_executions=100 retries=2 timeout_ms=30000 allow_untrusted_secret=false
# Strict execution recommended for production workflows:
#   export AETHERRA_SCRIPT_VERIFY_STRICT=1
#   export AETHERRA_SIGNING_STRICT=1
#   export AETHERRA_REQUIRE_CAPABILITIES=1
#   export AETHERRA_REQUIRE_STRICT=1
# Sign this file: python tools/sign_aether.py <file>.aether

# Dependencies
{requires}

# Workflow
narrate "Begin: {task}"
goal "{task}"
remember "Task initialized: {task}" as "init_{slug}"
# ... add steps here ...

narrate "Complete: {task}"
""".lstrip()

REQUIRES_STRICT = [
    'require module requests version="^2"',
]

REQUIRES_LENIENT = [
    "require module requests",
]


def slugify(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")


def load_custom_template() -> Optional[str]:
    """Return template text from AETHERRA_TEMPLATE_DIR if available, else None.

    Checks for template.aether then default.aether.
    """
    base = os.getenv("AETHERRA_TEMPLATE_DIR")
    if not base:
        return None
    for name in ("template.aether", "default.aether"):
        p = Path(base) / name
        try:
            if p.exists():
                return p.read_text(encoding="utf-8")
        except Exception:
            # Ignore and fallback
            continue
    return None


def _apply_placeholders(text: str, **mapping: str) -> str:
    """Safely replace {created},{task},{slug},{requires} without touching other braces.

    Avoids str.format so that literal JSON braces are preserved.
    """
    out = text
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="Short task description for the script header")
    ap.add_argument("--out", help="Output path (.aether)")
    args = ap.parse_args()

    created = datetime.utcnow().isoformat() + "Z"
    slug = slugify(args.task)[:40]
    # Auto-upgrade to strict requires if running in a production profile and not explicitly disabled.
    prod_like = (os.getenv("AETHERRA_PROFILE", "") or "").lower() in {
        "prod",
        "production",
    }
    strict_flag = os.getenv("AETHERRA_REQUIRE_STRICT")
    if prod_like and not strict_flag:
        # Implicitly enable strict for production safety; downstream tools may rely on this.
        os.environ["AETHERRA_REQUIRE_STRICT"] = "1"
        strict_flag = "1"

    requires = REQUIRES_STRICT if strict_flag == "1" else REQUIRES_LENIENT

    # Try custom template first
    raw_tpl = load_custom_template()
    if raw_tpl is None:
        raw_tpl = DEFAULT_TEMPLATE
    tpl = _apply_placeholders(
        raw_tpl,
        created=created,
        task=args.task,
        slug=slug,
        requires="\n".join(requires),
    )

    out_dir = Path("scripts")
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.out:
        out_file = Path(args.out)
    else:
        out_file = (
            out_dir
            / f"{created.replace(':', '').replace('-', '').replace('.', '')}_{slug}.aether"
        )

    out_file.write_text(tpl, encoding="utf-8")
    print(f"[CREATE] Wrote template: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
