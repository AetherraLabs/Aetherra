#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quality Gates Runner
- Dependency & security hygiene
- Tests with coverage & no-drop gate
- Optional architecture verification

Sequence:
 1. (Optional) Enforce dependency lock sync
 2. (Optional) Vulnerability scan (fails on severity threshold)
 3. Run tests with coverage & enforce no-drop
 4. (Optional) Architecture map verifier
 5. (Optional / non-fatal) License report artifact

Env/config:
    MIN_COVERAGE              : percentage (default 0; rely on no-drop unless overridden)
    COVERAGE_BASELINE_FILE    : path to store last coverage percent (default .coverage-baseline)
    TEST_TARGETS              : pytest target path(s). If unset, chooses existing from candidates.
    ARCH_CHECK                : 1 run architecture verifier (default 1)
    ARCH_CHECK_STRICT         : 1 fail gates if verifier non-zero (default 0)
    ARCH_PROBE_HUB            : 1 enable Hub probe (default 0)
    LOCK_ENFORCE              : 1 enforce requirements.lock drift check (default 1 if lock present)
    LOCK_FILE                 : path to lock file (default requirements.lock)
    VULN_SCAN                 : 1 run vulnerability scan (default 1 if lock present)
    VULN_FAIL_LEVEL           : severity threshold (default high) passed through to vuln_scan.py
    LICENSE_REPORT            : 1 generate license report (default 1)
    LICENSE_REPORT_JSON       : output JSON path (default licenses_report.json)
    LICENSE_DENY              : space/comma separated deny substrings (e.g. 'agpl GPL-2.0')
    LICENSE_FAIL_ON_UNKNOWN   : 1 to fail on UNKNOWN licenses (default 0)
    REQUIRE_THREAT_MODEL      : 1 require docs/THREAT_MODEL.md presence (default 1)
    REQUIRE_LICENSE_POLICY    : 1 require LICENSE_POLICY.md presence (default 1)
"""

# Standard library imports
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(cmd: list[str], timeout: float | None = None) -> tuple[int, str]:
    """Run a command and return (exit_code, stdout+stderr) decoded as UTF-8.

    Uses subprocess.run for improved timeout control and simpler IO.
    """
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return res.returncode, res.stdout
    except subprocess.TimeoutExpired as e:
        out = e.output or ""
        out += f"\n[TIMEOUT] Command exceeded {timeout}s: {' '.join(cmd)}"
        return 124, out


def run_optional_tool(label: str, args: list[str], fail_fatal: bool = True) -> bool:
    """Run a subordinate tool, printing output. Returns True if succeeded.

    If fail_fatal is False, failures are logged but do not abort gates.
    """
    print(f"[GATES] {label} -> {' '.join(args)}")
    code, out = run(args)
    print(out)
    if code != 0:
        msg = f"[GATES] {label} failed with exit {code}"
        if fail_fatal:
            print(msg)
            return False
        print(msg + " (non-fatal)")
    else:
        print(f"[GATES] {label} OK")
    return True


def parse_coverage(text: str) -> float | None:
    """
    Parse coverage percent from pytest-cov terminal report.
    Handles formats with columns:
    - Stmts  Miss  Cover
    - Stmts  Miss  Branch  BrPart  Cover
    """
    # Prefer the TOTAL line and capture the last percentage
    m = re.search(r"^TOTAL\b.*?(\d+)%\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not m:
        # Fallback: overall 'coverage: 97%'
        m = re.search(r"coverage[:\s]+(\d+)%", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def main() -> int:
    # Legacy hub enforcement removed - monolithic hub fully migrated to aetherra_hub module

    # Default strict license trend controls (can be overridden by CI env)
    os.environ.setdefault("LICENSE_UNKNOWN_TREND_FAIL", "1")
    os.environ.setdefault("LICENSE_UNKNOWN_TOLERANCE", "0")
    # Note: default 0 so we don't fail purely on threshold; we still enforce no-drop vs baseline.
    min_cov = float(os.getenv("MIN_COVERAGE", "0"))
    baseline_file = Path(os.getenv("COVERAGE_BASELINE_FILE", ".coverage-baseline"))
    raw_targets = os.getenv("TEST_TARGETS", "").strip()
    if raw_targets:
        targets = raw_targets.split()
    else:
        # Default: capabilities suite plus focused AAR/Outbox tests if present
        candidates = [
            "tests/capabilities",
            "tests/failure_injection",
            "tests/tools",
            "tests/test_outbox_unit.py",
            "tests/test_aar_outbox.py",
            "tests/test_agent_pipeline_smoke.py",
        ]
        # Ensure critical contract tests explicitly included if they exist
        contract_tests = [
            "tests/capabilities/test_diagnostics_schema.py",
            "tests/capabilities/test_plugin_parallel_and_failure_paths.py",
        ]
        for ct in contract_tests:
            if Path(ct).exists():
                candidates.append(ct)
        targets = [t for t in candidates if Path(t).exists()]
        # Fallback to tests/capabilities or tests if nothing found
        if not targets:
            targets = [
                t for t in ["tests/capabilities", "tests"] if Path(t).exists()
            ] or ["tests"]

    # 0. Dependency lock enforcement & vulnerability scan (pre-test)
    lock_file = Path(os.getenv("LOCK_FILE", "requirements.lock"))
    lock_exists = lock_file.exists()

    enforce_lock = os.getenv("LOCK_ENFORCE", "1") == "1" and lock_exists
    if enforce_lock:
        tool = Path("tools/enforce_lock_sync.py")
        if tool.exists():
            ok = run_optional_tool(
                "Lock Sync", [sys.executable, str(tool), "--lock", str(lock_file)]
            )
            if not ok:
                return 1
        else:
            print(
                "[GATES] Lock enforcement requested but tool missing; failing for safety."
            )
            return 1
    elif os.getenv("LOCK_ENFORCE", "1") == "1" and not lock_exists:
        # user expected enforcement but file absent
        print(f"[GATES] LOCK_ENFORCE=1 but missing {lock_file}; failing.")
        return 1
    else:
        print("[GATES] Lock enforcement skipped (disabled or lock absent)")

    vuln_scan_enabled = os.getenv("VULN_SCAN", "1") == "1" and lock_exists
    if vuln_scan_enabled:
        tool = Path("tools/vuln_scan.py")
        if tool.exists():
            args_vs = [sys.executable, str(tool), "--lock", str(lock_file)]
            fail_level = os.getenv("VULN_FAIL_LEVEL")
            if fail_level:
                args_vs += ["--fail-level", fail_level]
            ok = run_optional_tool("Vulnerability Scan", args_vs)
            if not ok:
                return 1
        else:
            print(
                "[GATES] Vulnerability scan requested but tool missing; continuing (treat as warning)."
            )
    else:
        print("[GATES] Vulnerability scan skipped (disabled or lock absent)")

    # Optional test selection heuristic (Phase 1 stub)
    selection_tool = Path("tools/test_selection_stub.py")
    selection_meta: dict | None = None
    if selection_tool.exists() and os.getenv("TEST_SELECTION", "1") == "1":
        touched_raw = os.getenv("TOUCHED_PATHS", "").strip()
        touched = [p for p in touched_raw.split() if p]
        sel_cmd = [sys.executable, str(selection_tool), *touched]
        print(f"[GATES] Running test selection stub: {' '.join(sel_cmd)}")
        code_sel, out_sel = run(sel_cmd)
        print(out_sel)
        if code_sel == 0:
            try:
                data_sel = json.loads(out_sel)
                selection_meta = data_sel
                candidates = data_sel.get("candidates") or []
                conf = float(data_sel.get("confidence", 0.0) or 0.0)
                if (
                    candidates
                    and not data_sel.get("fallback")
                    and conf >= float(os.getenv("TEST_SELECTION_MIN_CONF", "0.8"))
                ):
                    if 0 < len(candidates) < len(targets):
                        print(
                            f"[GATES] Adopting selected test subset ({len(candidates)} < {len(targets)}) with confidence {conf}"
                        )
                        targets = candidates
                else:
                    print(
                        f"[GATES] Ignoring selection subset (fallback or low confidence {conf}); running full targets"
                    )
            except Exception as e:  # pragma: no cover
                print(f"[GATES] Warning: cannot parse selection output: {e}\n{out_sel}")

    # 1. Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-o",
        "addopts=",
        "--maxfail=1",
        "--disable-warnings",
        "--cov=.",
        # Explicitly pass fail-under to override any config (pyproject/coverage) that might enforce a different value
        f"--cov-fail-under={int(min_cov)}",
        "--cov-report",
        "term",
    ] + targets
    code, out = run(cmd, timeout=float(os.getenv("TEST_TIMEOUT", "0")) or None)
    print(out)
    if code != 0:
        print("[GATES] Tests failed; gate failed.")
        return code

    cov = parse_coverage(out)
    if cov is None:
        print("[GATES] Could not parse coverage; failing to be safe.")
        return 1

    print(f"[GATES] Coverage: {cov}% (min {min_cov}%)")
    if cov < min_cov:
        print("[GATES] Coverage below minimum threshold.")
        return 1

    # Coverage no-drop gate
    prev = None
    if baseline_file.exists():
        try:
            prev = float(baseline_file.read_text().strip())
        except Exception:
            prev = None
    coverage_delta = None
    coverage_drop = False
    if prev is not None:
        coverage_delta = cov - prev
        if cov < prev:
            coverage_drop = True
            print(f"[GATES] Coverage dropped: prev {prev}% -> now {cov}%")
            # Do not return yet; gather gating reasons for JSON report then fail.

    # Update baseline to latest
    if not coverage_drop:  # Only update baseline if not a regression
        try:
            baseline_file.write_text(str(cov))
        except Exception as e:
            print(f"[GATES] Warning: failed to write baseline: {e}")

    # ------------------------------------------------------------------
    # Per-file coverage delta artifact (experimental Phase 1 extension)
    # ------------------------------------------------------------------
    file_deltas: list[dict] = []
    file_drop_entries: list[dict] = []
    per_file_enabled = os.getenv("COVERAGE_FILE_LEVEL", "1") == "1"
    coverage_json_path = Path("coverage.json")
    previous_snapshot: dict[str, float] = {}
    previous_snapshot_path = None
    if per_file_enabled:
        # Attempt to create coverage.json if not present (coverage json command)
        if not coverage_json_path.exists():
            try:
                code_cov_json, out_cov_json = run(
                    [sys.executable, "-m", "coverage", "json", "-o", "coverage.json"],
                    timeout=120,
                )
                if code_cov_json != 0:
                    print(
                        "[GATES] Warning: coverage json generation failed; skipping per-file deltas"
                    )
            except Exception as e:  # pragma: no cover
                print(f"[GATES] Warning: exception generating coverage json: {e}")
        if coverage_json_path.exists():
            try:
                cov_data = json.loads(coverage_json_path.read_text(encoding="utf-8"))
            except Exception as e:  # pragma: no cover
                cov_data = {}
                print(f"[GATES] Warning: failed to parse coverage.json: {e}")
            # Load previous artifact (latest by name) if any
            snapshots_dir = Path("audit/coverage_delta")
            if snapshots_dir.is_dir():
                try:
                    snaps = sorted(snapshots_dir.glob("*.json"))
                    if snaps:
                        previous_snapshot_path = snaps[-1]
                        try:
                            prev_data = json.loads(
                                previous_snapshot_path.read_text(encoding="utf-8")
                            )
                            for f in prev_data.get("files", []):
                                previous_snapshot[str(f.get("path"))] = float(
                                    f.get("after")
                                    or f.get("percent_after")
                                    or f.get("percent", 0.0)
                                )
                        except Exception as e:  # pragma: no cover
                            print(
                                f"[GATES] Warning: could not load previous coverage snapshot: {e}"
                            )
                except Exception:
                    pass
            files_section = cov_data.get("files") if isinstance(cov_data, dict) else {}
            # Determine changed files heuristic: TOUCHED_PATHS env or git diff HEAD~1
            changed_files: set[str] = set()
            touched_raw = os.getenv("TOUCHED_PATHS", "").strip()
            if touched_raw:
                changed_files.update(
                    [p for p in touched_raw.split() if p.endswith(".py")]
                )
            if not changed_files:
                try:
                    code_diff, out_diff = run(
                        [
                            "git",
                            "--no-pager",
                            "diff",
                            "--name-only",
                            "HEAD~1",
                        ],
                        timeout=15,
                    )
                    if code_diff == 0:
                        for line in out_diff.splitlines():
                            if line.endswith(".py"):
                                changed_files.add(line.strip())
                except Exception:  # pragma: no cover
                    pass
            # Fallback: consider all files in coverage data
            if not changed_files and isinstance(files_section, dict):
                changed_files.update(files_section.keys())
            for path_key, info in (files_section or {}).items():
                try:
                    summary = info.get("summary", {}) if isinstance(info, dict) else {}
                    covered = float(summary.get("covered_lines", 0) or 0)
                    stmts = float(summary.get("num_statements", 0) or 0)
                    after_pct = (covered / stmts * 100.0) if stmts > 0 else 0.0
                    before_pct = previous_snapshot.get(path_key)
                    delta_pct = None
                    if before_pct is not None:
                        delta_pct = after_pct - before_pct
                    entry = {
                        "path": path_key,
                        "before": before_pct,
                        "after": after_pct,
                        "delta": delta_pct,
                        "changed": path_key in changed_files,
                    }
                    file_deltas.append(entry)
                    if (delta_pct is not None) and delta_pct < 0:
                        file_drop_entries.append(entry)
                except Exception as e:  # pragma: no cover
                    print(
                        f"[GATES] Warning: per-file coverage entry parse failed for {path_key}: {e}"
                    )
            # Write snapshot artifact
            try:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                out_dir = Path("audit/coverage_delta")
                out_dir.mkdir(parents=True, exist_ok=True)
                snapshot_path = out_dir / f"coverage_{ts}.json"
                snapshot_doc = {
                    "run_id": ts,
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "overall": {"after": cov, "before": prev, "delta": coverage_delta},
                    "files": file_deltas,
                }
                snapshot_path.write_text(
                    json.dumps(snapshot_doc, indent=2), encoding="utf-8"
                )
                print(f"[GATES] Wrote per-file coverage snapshot -> {snapshot_path}")
                # Retention
                retention = int(os.getenv("COVERAGE_FILE_RETENTION", "30"))
                snaps_all = sorted(out_dir.glob("coverage_*.json"))
                if len(snaps_all) > retention:
                    for old in snaps_all[:-retention]:
                        try:
                            old.unlink()
                        except Exception:
                            pass
                # Optional orphan pruning of legacy root coverage.json files
                if os.getenv("COVERAGE_PRUNE_ORPHANS", "1") == "1":
                    try:
                        root_cov = Path("coverage.json")
                        # If a root coverage.json exists and we now have at least one snapshot, remove it
                        if root_cov.exists() and snaps_all:
                            root_cov.unlink()
                            print(
                                "[GATES] Pruned orphan root coverage.json (snapshots in use)."
                            )
                    except Exception as e:  # pragma: no cover
                        print(
                            f"[GATES] Warning: failed pruning orphan coverage.json: {e}"
                        )
            except Exception as e:  # pragma: no cover
                print(f"[GATES] Warning: failed to write coverage delta snapshot: {e}")

    # Security & memory fragmentation supplemental gates (post-tests so new tools are importable)
    # Additional lightweight security / policy guards
    #  - repo_security_scan: heuristic scan for risky primitives
    #  - ci_verify_no_discord_bot: ensure internal Discord bot excluded
    #  - ci_verify_no_website_artifacts: ensure website build artifacts not committed
    if os.getenv("REPO_SECURITY_SCAN", "1") == "1":
        scan_script = Path("tools/repo_security_scan.py")
        if scan_script.exists():
            print("[GATES] Running repo_security_scan (heuristic risk scan)...")
            code_repo, out_repo = run([sys.executable, str(scan_script)], timeout=120)
            print(out_repo)
            if code_repo != 0 and os.getenv("REPO_SECURITY_STRICT", "1") == "1":
                print("[GATES] repo_security_scan reported high severity findings.")
                return 1
        else:
            print("[GATES] repo_security_scan.py missing; skipping.")
    if os.getenv("DISCORD_EXCLUSION_CHECK", "1") == "1":
        discord_guard = Path("tools/ci_verify_no_discord_bot.py")
        if discord_guard.exists():
            code_disc, out_disc = run([sys.executable, str(discord_guard)], timeout=60)
            print(out_disc)
            if code_disc != 0:
                print("[GATES] Discord exclusion guard failed.")
                return 1
        else:
            # Fallback to legacy guard if present
            legacy_guard = Path("tools/guard_discord_exclusion.py")
            if legacy_guard.exists():
                code_disc, out_disc = run(
                    [sys.executable, str(legacy_guard)], timeout=60
                )
                print(out_disc)
                if code_disc != 0:
                    print("[GATES] Legacy discord exclusion guard failed.")
                    return 1
            else:
                print("[GATES] No discord exclusion guard script found.")
    if os.getenv("WEBSITE_ARTIFACT_CHECK", "1") == "1":
        site_guard = Path("tools/ci_verify_no_website_artifacts.py")
        if site_guard.exists():
            code_site, out_site = run([sys.executable, str(site_guard)], timeout=60)
            print(out_site)
            if code_site != 0:
                print("[GATES] Website artifact guard failed.")
                return 1
        else:
            print("[GATES] ci_verify_no_website_artifacts.py missing; skipping.")
    if os.getenv("STATIC_SECURITY_SCAN", "1") == "1":
        scan_tool = Path("tools/static_security_scan.py")
        if scan_tool.exists():
            print("[GATES] Running static security scan (fail on critical findings)...")
            code_scan, out_scan = run(
                [
                    sys.executable,
                    str(scan_tool),
                    "--root",
                    ".",
                    "--json",
                    "security_scan_report.json",
                    "--md",
                    "security_scan_report.md",
                ],
                timeout=300,
            )
            print(out_scan)
            if code_scan != 0:
                print("[GATES] Static security scan failed (critical findings).")
                return 1
        else:
            print("[GATES] static_security_scan.py missing; skipping (non-fatal).")

    if os.getenv("FRAGMENTATION_CHECK", "1") == "1":
        frag_tool = Path("tools/memory_fragmentation_metrics.py")
        if frag_tool.exists():
            print("[GATES] Measuring memory fragmentation heuristic...")
            # Run tool as a module to print dict; capture output
            code_frag, out_frag = run([sys.executable, str(frag_tool)])
            print(out_frag)
            # Attempt to parse dict literal (safe eval using json after replacement)
            # Standard library imports
            import json as _json
            import re as _re

            stats_match = _re.search(r"\{.*\}", out_frag, _re.S)
            if stats_match:
                try:
                    # Replace single quotes if present to be JSON compliant
                    raw = stats_match.group(0).replace("'", '"')
                    stats = _json.loads(raw)
                    ratio_before = float(
                        stats.get("fragmentation_ratio_before", 0.0) or 0.0
                    )
                    ratio_after = float(
                        stats.get("fragmentation_ratio_after", 0.0) or 0.0
                    )
                    allowed_delta = float(
                        os.getenv("FRAGMENTATION_ALLOWED_DELTA", "0.30")
                    )
                    delta = max(0.0, ratio_after - ratio_before)
                    print(
                        f"[GATES] Fragmentation ratios before={ratio_before:.4f} after={ratio_after:.4f} delta={delta:.4f} (allowed <= {allowed_delta})"
                    )
                    if delta > allowed_delta:
                        print("[GATES] Fragmentation delta exceeds allowed threshold.")
                        return 1
                except Exception as e:  # pragma: no cover
                    print(f"[GATES] Warning: failed to parse fragmentation stats: {e}")
            else:
                print(
                    "[GATES] Warning: could not locate fragmentation stats in output."
                )
        else:
            print(
                "[GATES] memory_fragmentation_metrics.py missing; skipping (non-fatal)."
            )

    # 2. Optional: run Architecture Map verifier
    if os.getenv("ARCH_CHECK", "1") == "1":
        strict = os.getenv("ARCH_CHECK_STRICT", "0") == "1"
        probe = os.getenv("ARCH_PROBE_HUB", "0") == "1"
        args = [sys.executable, "-X", "utf8", "tools/verify_architecture_map.py"]
        if strict:
            args.append("--strict")
        if probe:
            args.append("--probe-hub")
        print("[GATES] Running Architecture Map verifier...")
        code_arch, out_arch = run(args)
        print(out_arch)
        if code_arch != 0 and strict:
            print("[GATES] Architecture verifier failed in strict mode.")
            return code_arch

    # 3. Optional: license report (can be fatal if policy set)
    if os.getenv("LICENSE_REPORT", "1") == "1":
        tool = Path("tools/license_report.py")
        if tool.exists() and lock_exists:
            json_out = os.getenv("LICENSE_REPORT_JSON", "licenses_report.json")
            deny_raw = os.getenv("LICENSE_DENY", "").replace(",", " ")
            deny_parts = [d for d in deny_raw.split() if d]
            args_lr = [
                sys.executable,
                str(tool),
                "--lock",
                str(lock_file),
                "--json",
                json_out,
            ]
            if deny_parts:
                args_lr += ["--deny", *deny_parts]
            fail_unknown = os.getenv("LICENSE_FAIL_ON_UNKNOWN", "0") == "1"
            if fail_unknown:
                args_lr.append("--fail-on-unknown")
            fatal = bool(deny_parts) or fail_unknown
            ok = run_optional_tool("License Report", args_lr, fail_fatal=fatal)
            if not ok and fatal:
                return 1
            # Run non-fatal policy enforcement right after report generation to surface UNKNOWN metrics.
            enforce_tool = Path("tools/enforce_license_policy.py")
            if enforce_tool.is_file():
                # Decide if enforcement should be fatal based on env signals.
                trend_fail = os.getenv("LICENSE_UNKNOWN_TREND_FAIL", "0") == "1"
                abs_max_set = bool(
                    os.getenv("LICENSE_UNKNOWN_FAIL_IF_GT")
                    or os.getenv("LICENSE_UNKNOWN_ABS_MAX")
                )
                # Auto-tighten: if no explicit ABS_MAX provided but we have a fresh report with zero UNKNOWN, set ABS_MAX=0
                auto_fail_on_unknown = False
                if not abs_max_set:
                    try:
                        report_json = Path(json_out)
                        if report_json.exists():
                            # Standard library imports
                            import json as _json

                            data = _json.loads(report_json.read_text(encoding="utf-8"))
                            unknown_present = any(
                                (r.get("license") or "").strip().upper() == "UNKNOWN"
                                for r in data
                            )
                            if not unknown_present:
                                # tighten baseline automatically
                                os.environ.setdefault("LICENSE_UNKNOWN_ABS_MAX", "0")
                                abs_max_set = True
                                auto_fail_on_unknown = True
                                print(
                                    "[GATES] Auto-set LICENSE_UNKNOWN_ABS_MAX=0 (no UNKNOWN licenses present)"
                                )
                    except Exception as e:  # pragma: no cover
                        print(f"[GATES] Auto-tighten check failed: {e}")
                # Defense-in-depth: if ABS_MAX=0 (auto or explicit) and we didn't already request fail-on-unknown, run a second pass check.
                if (
                    os.getenv("LICENSE_UNKNOWN_ABS_MAX") == "0" or auto_fail_on_unknown
                ) and "--fail-on-unknown" not in args_lr:
                    # Re-run lightweight validation using license_report with fail flag (non-fatal here if enforcement will catch issues)
                    args_lr_fail = [
                        sys.executable,
                        str(tool),
                        "--lock",
                        str(lock_file),
                        "--json",
                        json_out,
                        "--fail-on-unknown",
                    ]
                    run_optional_tool(
                        "License Report (fail-on-unknown confirm)",
                        args_lr_fail,
                        fail_fatal=False,
                    )
                fail_fatal = trend_fail or abs_max_set
                args_enforce = [sys.executable, str(enforce_tool)]
                os.environ["LICENSE_REPORT_JSON"] = json_out
                run_optional_tool(
                    "License Policy Enforcement", args_enforce, fail_fatal=fail_fatal
                )
            else:
                print(
                    "[GATES] License enforcement script missing (tools/enforce_license_policy.py); skipping (non-fatal)"
                )
        else:
            print("[GATES] License report skipped (tool or lock missing)")

        # SBOM generation (non-fatal; provides artifact for supply-chain transparency)
        if os.getenv("SBOM_GENERATE", "1") == "1":
            sbom_tool = Path("tools/generate_sbom.py")
            if sbom_tool.exists() and lock_exists:
                run_optional_tool(
                    "SBOM Generate",
                    [
                        sys.executable,
                        str(sbom_tool),
                        "--license-json",
                        os.getenv("LICENSE_REPORT_JSON", "licenses_report.json"),
                        "--out",
                        os.getenv("SBOM_OUT", "sbom.json"),
                    ],
                    fail_fatal=False,
                )
            else:
                print("[GATES] SBOM generation skipped (tool or lock missing)")

    # 4. Threat model presence enforcement
    if os.getenv("REQUIRE_THREAT_MODEL", "1") == "1":
        if not Path("docs/THREAT_MODEL.md").exists():
            print("[GATES] Missing docs/THREAT_MODEL.md (REQUIRE_THREAT_MODEL=1)")
            return 1

    # 5. License policy presence (non-negotiable for alpha governance transparency)
    if os.getenv("REQUIRE_LICENSE_POLICY", "1") == "1":
        if not Path("LICENSE_POLICY.md").exists():
            print("[GATES] Missing LICENSE_POLICY.md (REQUIRE_LICENSE_POLICY=1)")
            return 1

    # 6. Packaging smoke test (build + install + basic probes)
    if os.getenv("PACKAGE_SMOKE", "1") == "1":
        smoke = Path("tools/packaging_smoke.py")
        if smoke.exists():
            ok = run_optional_tool("Packaging Smoke", [sys.executable, str(smoke)])
            if not ok:
                return 1
        else:
            print("[GATES] Packaging smoke script missing (non-fatal)")

    # Placeholder for future strict enforcement (Beta toggle)
    if os.getenv("LICENSE_POLICY_STRICT", "0") == "1":  # future use
        print(
            "[GATES] LICENSE_POLICY_STRICT=1 set but strict implementation not yet available; proceeding (info)"
        )

    # 7. Artifact publish staging (non-fatal): collects key outputs for CI upload
    if os.getenv("PUBLISH_ARTIFACTS", "1") == "1":
        artifacts_dir = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
        artifacts_dir.mkdir(exist_ok=True)
        candidate_paths: list[Path] = [
            Path("licenses_report.json"),
            Path(os.getenv("SBOM_OUT", "sbom.json")),
            Path("integrity-manifest.json"),
            Path("requirements.lock"),
        ]
        copied = 0
        for c in candidate_paths:
            if c.exists():
                try:
                    target = artifacts_dir / c.name
                    target.write_bytes(c.read_bytes())
                    copied += 1
                except Exception as e:  # pragma: no cover - FS issues
                    print(f"[GATES] Artifact copy failed for {c}: {e}")
        print(f"[GATES] Staged {copied} artifact files in {artifacts_dir}")
    else:
        print("[GATES] Artifact publishing disabled (PUBLISH_ARTIFACTS=0)")

    # Consolidated gating reasons & metrics export
    gating_reasons: list[dict] = []
    if coverage_drop:
        gating_reasons.append(
            {
                "code": "COVERAGE_DROP",
                "severity": "error",
                "message": f"Coverage decreased from {prev}% to {cov}%",
            }
        )
    if selection_meta:
        gating_reasons.append(
            {
                "code": "TEST_SELECTION",
                "severity": "info",
                "message": f"Strategy {selection_meta.get('strategy')} confidence={selection_meta.get('confidence')} fallback={selection_meta.get('fallback')}",
            }
        )
    # File-level regression reasons (limit to first 5)
    for entry in file_drop_entries[:5]:
        try:
            gating_reasons.append(
                {
                    "code": "FILE_COVERAGE_DROP",
                    "severity": "warning" if not coverage_drop else "error",
                    "message": f"{entry['path']} {entry['delta']:.2f}% ({entry['before']} -> {entry['after']})",
                }
            )
        except Exception:
            pass
    # Future: append reasons for vuln scan, arch failures, etc.

    coverage_report_path = Path(
        os.getenv("COVERAGE_REPORT_JSON", "coverage_gate_report.json")
    )
    # Schema versioning: v1 introduces explicit schema_version plus future flags to allow
    # forward-compatible evolution (see ADR-0003). "future" keys are placeholders that
    # downstream tools can probe for to adapt once populated.
    report = {
        "schema_version": 1,
        "coverage": cov,
        "previous": prev,
        "delta": coverage_delta,
        "min_threshold": min_cov,
        "drop": coverage_drop,
        "updated_baseline": not coverage_drop,
        "gating_reasons": gating_reasons,
        "selection": selection_meta,
        "file_deltas": file_deltas if per_file_enabled else None,
        "targets": targets,
        # Future flags (reserved): will flip true once branch / statement granularity enforced.
        "future": {
            "enforce_branch_coverage": False,
            "enforce_statement_coverage": False,
        },
    }
    try:
        coverage_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[GATES] Wrote coverage gate report -> {coverage_report_path}")
    except Exception as e:  # pragma: no cover
        print(f"[GATES] Warning: failed to write coverage report: {e}")

    # Optional PR description generation (lightweight) using gating report contents.
    if os.getenv("GENERATE_PR_DESCRIPTION", "0") == "1":
        try:
            pr_path = Path(os.getenv("PR_DESCRIPTION_PATH", "pr_description.md"))
            lines: list[str] = []
            lines.append("# Quality Gates Summary\n")
            status = "FAIL" if coverage_drop else "PASS"
            lines.append(
                f"Overall Coverage: {cov:.2f}% (prev {prev:.2f}% delta {coverage_delta:+.2f}%)  "
                + f"Gate Result: {status}\n"
            )
            lines.append(f"Schema Version: {report.get('schema_version', 1)}\n")
            # Gating reasons table
            reasons = gating_reasons
            if reasons:
                lines.append("## Gating Reasons\n")
                lines.append("| Code | Severity | Message |\n")
                lines.append("|------|----------|---------|\n")
                for r in reasons:
                    lines.append(
                        f"| {r.get('code')} | {r.get('severity')} | {r.get('message', '').replace('|', '/')} |\n"
                    )
            # File coverage deltas summary
            file_deltas = report.get("file_deltas")
            if file_deltas and isinstance(file_deltas, list):
                drops = [
                    d
                    for d in file_deltas
                    if isinstance(d, dict)
                    and d.get("delta") is not None
                    and d["delta"] < 0
                ]
                improves = [
                    d
                    for d in file_deltas
                    if isinstance(d, dict)
                    and d.get("delta") is not None
                    and d["delta"] > 0
                ]
                drops.sort(key=lambda x: x["delta"])
                improves.sort(key=lambda x: x["delta"], reverse=True)
                if drops:
                    lines.append("\n### Top File Coverage Drops\n")
                    for d in drops[:5]:
                        lines.append(
                            f"* {d['path']}: {d['before']:.2f}% -> {d['after']:.2f}% ({d['delta']:+.2f}%)"
                        )
                if improves:
                    lines.append("\n### Top File Coverage Improvements\n")
                    for d in improves[:5]:
                        lines.append(
                            f"* {d['path']}: {d['before']:.2f}% -> {d['after']:.2f}% ({d['delta']:+.2f}%)"
                        )
            # Future flags exposure
            fut = report.get("future", {})
            if fut and isinstance(fut, dict):
                lines.append("\n### Future Flags\n")
                for k, v in fut.items():
                    lines.append(f"* {k}: {v}")
            pr_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"[GATES] Wrote PR description -> {pr_path}")
        except Exception as e:  # pragma: no cover
            print(f"[GATES] Warning: failed to generate PR description: {e}")

    if coverage_drop:
        print("[GATES] Gate failure due to coverage drop.")
        return 1

    print("[GATES] All quality gates passed.")
    # Optional Prometheus metrics validation (after other gates succeed)
    if os.getenv("CONSCIOUSNESS_METRICS_CHECK", "0") == "1":
        # Standard library imports
        import time
        import urllib.request

        host = os.getenv("CONSCIOUSNESS_METRICS_HOST", "http://localhost")
        port = int(os.getenv("AETHERRA_PROM_PORT", "9109"))
        url = f"{host}:{port}/metrics"
        # Always-required base metrics
        required_base = {
            "aetherra_consciousness_workspace_queue_size": "gauge",
            "aetherra_consciousness_narrative_coherence": "gauge",
        }
        # New detailed metrics (strict mode or informational if not strict)
        detailed_expected = {
            "aetherra_consciousness_workspace_candidates_total": "counter",
            "aetherra_consciousness_workspace_broadcasts_total": "counter",
            "aetherra_consciousness_workspace_latency_seconds": "histogram",
            "aetherra_consciousness_narrative_generation_seconds": "histogram",
            # chapters gauge is informative (may remain 0); keep in detailed by default
            "aetherra_consciousness_narrative_chapters_total": "gauge",
        }
        strict = os.getenv("CONSCIOUSNESS_METRICS_STRICT", "0") == "1"
        require_samples = os.getenv("CONSCIOUSNESS_METRICS_REQUIRE_SAMPLES", "0") == "1"
        expect_sources_raw = os.getenv(
            "CONSCIOUSNESS_METRICS_EXPECT_SOURCE", ""
        ).strip()
        expect_sources = [s for s in re.split(r"[,\s]+", expect_sources_raw) if s]

        # brief wait for exporter startup + small retry loop
        body = ""
        for _attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:  # nosec B310
                    body = resp.read().decode("utf-8", errors="replace")
                if body:
                    break
            except Exception as exc:
                print(f"[GATES] Metrics fetch attempt failed: {exc}")
            time.sleep(0.5)
        if not body:
            print("[GATES] Consciousness metrics endpoint not reachable.")
            return 1

        # Parse TYPE declarations for stronger validation
        type_map: dict[str, str] = {}
        try:
            for line in body.splitlines():
                # Example: '# TYPE aetherra_consciousness_workspace_queue_size gauge'
                line = line.strip()
                if line.startswith("# TYPE "):
                    parts = line.split()
                    if len(parts) >= 4:
                        metric, mtype = parts[2], parts[3]
                        type_map[metric] = mtype
        except Exception:
            type_map = {}

        def present(metric: str) -> bool:
            # Accept presence either via TYPE line or raw metric occurrences (for _bucket/_sum etc.)
            if metric in type_map:
                return True
            return (metric in body) or any(
                (metric + suffix) in body for suffix in ("_bucket", "_sum", "_count")
            )

        def has_sample(metric: str) -> bool:
            """Detect if there is at least one emitted sample line for the metric.
            For histograms/counters, look for *_count or labeled lines; for gauges, allow bare value lines.
            """
            for line in body.splitlines():
                if line.startswith(metric + "{") or line.startswith(metric + " "):
                    return True
                if metric.endswith("_seconds") and (
                    line.startswith(metric + "_count")
                    or line.startswith(metric + "_sum")
                ):
                    return True
            return False

        def has_source_label(metric: str, source_value: str) -> bool:
            needle = f'{metric}{{source="{source_value}"}}'
            return needle in body

        missing_base = [m for m in required_base if not present(m)]
        if missing_base:
            print(
                f"[GATES] Consciousness metrics check FAILED missing base metrics: {', '.join(missing_base)}"
            )
            return 1

        # For detailed metrics, warn if missing unless strict
        missing_detailed = [m for m in detailed_expected if not present(m)]
        type_mismatches: list[str] = []
        # Validate expected types when available
        for m, expected_type in {**required_base, **detailed_expected}.items():
            actual = type_map.get(m)
            if actual and actual != expected_type:
                type_mismatches.append(f"{m} (expected {expected_type}, got {actual})")

        if type_mismatches:
            msg = ", ".join(type_mismatches)
            if strict:
                print(f"[GATES] Metrics TYPE mismatch (strict): {msg}")
                return 1
            print(f"[GATES] Warning: metrics TYPE mismatch: {msg}")

        if missing_detailed:
            if strict:
                print(
                    f"[GATES] Consciousness detailed metrics missing (strict): {', '.join(missing_detailed)}"
                )
                return 1
            print(
                f"[GATES] Info: detailed metrics not all present: {', '.join(missing_detailed)}"
            )
        else:
            print("[GATES] Consciousness detailed metrics present.")

        # Optional: require that detailed metrics emit at least one sample (guards against registry init without updates)
        if require_samples:
            sample_missing: list[str] = []
            for m in detailed_expected:
                if not has_sample(m):
                    sample_missing.append(m)
            if sample_missing:
                msg = f"Detailed metrics missing samples: {', '.join(sample_missing)}"
                if strict:
                    print(f"[GATES] {msg} (strict)")
                    return 1
                print(f"[GATES] Warning: {msg}")

        # Optional: expected source labels must appear on counters
        if expect_sources:
            missing_sources: list[str] = []
            for sv in expect_sources:
                has_any = has_source_label(
                    "aetherra_consciousness_workspace_candidates_total", sv
                ) or has_source_label(
                    "aetherra_consciousness_workspace_broadcasts_total", sv
                )
                if not has_any:
                    missing_sources.append(sv)
            if missing_sources:
                msg = (
                    f"Expected source labels not observed: {', '.join(missing_sources)}"
                )
                if strict:
                    print(f"[GATES] {msg} (strict)")
                    return 1
                print(f"[GATES] Info: {msg}")
        print("[GATES] Consciousness metrics check OK (base metrics present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
