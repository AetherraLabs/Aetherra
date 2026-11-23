#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Aetherra Labs and Contributors

"""Verify the bounded company-website cleanup against its pre-migration commit.

Run from any directory with Python 3.10+ and a full Git checkout. This is a
one-time migration check, not a restriction on future software development.
It reads the baseline tree from Git instead of committing a repository inventory.
"""

from __future__ import annotations

# Standard library imports
import argparse
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "645ab2ed5cccb3c1d26fb4eac414ac7640d6dd96"
RETIRED_PATHS = {
    ".github/workflows/deploy-pages.yml",
    "docs/404.html",
    "docs/CNAME",
    "docs/index.html",
    "docs/assets/ibm-plex-mono-latin-400-normal-CvHOgSBP.woff",
    "docs/assets/ibm-plex-mono-latin-400-normal-DMJ8VG8y.woff2",
    "docs/assets/index-C-Fa0ZPS.css",
    "docs/assets/index-CE-hCudL.css",
    "docs/assets/index-Cjaivu43.css",
    "docs/assets/index-DCpsYfW3.js",
    "docs/assets/index-DMShYv1G.js",
    "docs/assets/index-DY_WARk-.js",
    "docs/assets/index-OrXyYuWD.js",
    "docs/assets/index-klotJSoy.js",
    "docs/assets/instrument-sans-latin-wght-normal-BbzFLZTg.woff2",
    "docs/assets/instrument-serif-latin-400-italic-DKMiL14s.woff2",
    "docs/assets/instrument-serif-latin-400-italic-u__WvvIK.woff",
    "docs/branding/favicon.png",
    "docs/branding/font-licenses.txt",
    "docs/branding/nav-icon.webp",
    "docs/favicon.svg",
    "docs/media/orbital-weave.webp",
    "docs/media/projects/aetherra.webp",
    "docs/media/projects/aevryn.webp",
    "docs/media/projects/rbxl.webp",
    "docs/media/projects/rogue.webp",
    "scripts/devops/build-website.bat",
    "scripts/devops/build-website.sh",
    "scripts/devops/dev-website.bat",
    "scripts/devops/dev-website.sh",
}
HTML_CONSUMERS = {
    "docs/community/code-of-conduct.html",
    "docs/community/rfc.html",
    "docs/help/hub.html",
    "docs/labs/notes.html",
    "docs/labs/replication-kit.html",
    "docs/research/cite.html",
    "docs/research/view.html",
    "docs/sections/aether-language.html",
    "docs/sections/api-registry.html",
    "docs/sections/changelog-versioning.html",
    "docs/sections/developers.html",
    "docs/sections/hub.html",
    "docs/sections/memory-cognition.html",
    "docs/sections/ops-security.html",
    "docs/sections/plugin-authors.html",
    "docs/sections/plugin-sdk.html",
    "docs/sections/researchers.html",
    "docs/sections/runtime-cli.html",
    "docs/sections/safety-ethics.html",
    "docs/sections/tutorials-recipes.html",
}
ASSET_MOVES = {
    "docs/assets/index-C-Fa0ZPS.css": "docs/sections/documentation-base.css",
    "docs/favicon.svg": "docs/sections/documentation-icon.svg",
}
URL_REPLACEMENTS = {
    "/assets/index-C-Fa0ZPS.css": "/sections/documentation-base.css",
    "/favicon.svg": "/sections/documentation-icon.svg",
}
ALLOWED_CHANGES = (
    RETIRED_PATHS
    | HTML_CONSUMERS
    | set(ASSET_MOVES.values())
    | {
        ".github/PAGES_STATUS.md",
        "docs/ops/README_DEPLOY.md",
        "docs/sections/section-theme.js",
        "tools/verify_website_migration.py",
    }
)
# This reference was already broken before the migration. Do not silently fix
# unrelated technical content as part of retiring the company publisher.
EXISTING_BROKEN_LINKS = {
    ("docs/community/rfc.html", "/docs/ARCHITECTURE_VALIDATION_REPORT.md"),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


class Resources(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.urls.append(value)


def verify(baseline: str) -> list[str]:
    failures: list[str] = []
    changed = set(
        git(
            "diff", "--no-ext-diff", "--no-renames", "--name-only", "-z", baseline, "--"
        )
        .decode("utf-8")
        .rstrip("\0")
        .split("\0")
    ) - {""}
    for path in sorted(changed - ALLOWED_CHANGES):
        failures.append(f"Nonallowlisted baseline file changed: {path}")
    for path in sorted(RETIRED_PATHS):
        if (ROOT / path).exists():
            failures.append(f"Retired company file is still present: {path}")

    for old, new in ASSET_MOVES.items():
        path = ROOT / new
        if not path.is_file():
            failures.append(f"Missing documentation asset: {new}")
            continue
        # Compare Git blobs with Git's normal checkout filters (e.g. CRLF).
        expected = git("rev-parse", f"{baseline}:{old}").strip()
        actual = git("hash-object", f"--path={old}", new).strip()
        if actual != expected:
            failures.append(f"Moved documentation asset differs from baseline: {new}")

    for name in sorted(HTML_CONSUMERS):
        path = ROOT / name
        if not path.is_file():
            failures.append(f"Technical HTML was removed: {name}")
            continue
        expected = git("show", f"{baseline}:{name}").decode("utf-8")
        for old, new in URL_REPLACEMENTS.items():
            expected = expected.replace(old, new)
        if path.read_text(encoding="utf-8") != expected.replace("\r\n", "\n"):
            failures.append(f"Technical HTML changed beyond asset references: {name}")

    for path in sorted((ROOT / "docs").rglob("*.html")):
        if "_build" in path.parts:
            continue
        name = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        for retired in URL_REPLACEMENTS:
            if retired in source:
                failures.append(f"Retired asset reference in {name}: {retired}")
        parser = Resources()
        parser.feed(source)
        for url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            if (name, parts.path) in EXISTING_BROKEN_LINKS or parts.path == "/":
                continue
            target = (
                ROOT / "docs" / unquote(parts.path.lstrip("/"))
                if parts.path.startswith("/")
                else path.parent / unquote(parts.path)
            )
            if not target.exists():
                failures.append(f"Missing local HTML resource in {name}: {url}")

    theme = (ROOT / "docs/sections/section-theme.js").read_text(encoding="utf-8")
    if "iframe" in theme or "cloneNode" in theme:
        failures.append("Documentation navigation still clones the company homepage")
    if 'class="brand" href="/sections/hub.html"' not in theme:
        failures.append("Documentation navigation brand does not link to the docs hub")
    for function in ("setupCopy", "injectBreadcrumb"):
        if f"function {function}()" not in theme:
            failures.append(f"Documentation support behavior was removed: {function}")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE, help="Pre-migration Git commit")
    args = parser.parse_args()
    try:
        failures = verify(args.baseline)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"[website-migration] FAIL: {error}")
        return 1
    if failures:
        for failure in failures:
            print(f"[website-migration] FAIL: {failure}")
        return 1
    print(
        "[website-migration] OK: company artifacts absent; technical content, "
        "resources and all nonallowlisted baseline blobs preserved"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
