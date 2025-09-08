"""Code Operations Engine (Phase 0 skeleton)

Responsibilities (future):
  - File graph modeling
  - Patch composition & reversible diffs
  - Refactor engine integration
  - Formatting / lint adapters

Current minimal implementation provides helper builders and a unified diff applier
with dry-run and rollback token generation.
"""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PatchApplyResult:
    applied: bool
    diff: str
    dry_run: bool
    rollback_token: str | None
    diagnostics: list[str]


def build_new_file_diff(path: Path, content: str) -> str:
    return f"*** Begin Patch\n*** Add File: {path}\n{content}\n*** End Patch"


def build_comment_insertion_diff(path: Path, comment: str) -> str:
    original = path.read_text(encoding="utf-8", errors="replace")
    header = f"# {comment}\n"
    new_content = header + original
    diff_lines = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
    )
    patch = (
        ["*** Begin Patch", f"*** Update File: {path}"] + diff_lines + ["*** End Patch"]
    )
    return "\n".join(patch)


def apply_unified_diff(
    diff_text: str, repo_root: Path, dry_run: bool = False
) -> PatchApplyResult:
    diagnostics: list[str] = []
    applied_files: list[Path] = []
    lines = diff_text.splitlines()
    i = 0
    current_file: Path | None = None
    mode: str | None = None  # update|add
    file_original: str | None = None
    file_new: list[str] | None = None
    while i < len(lines):
        line = lines[i]
        if line.startswith("*** Update File:"):
            if (
                current_file
                and mode == "update"
                and file_new is not None
                and not dry_run
            ):
                _write_if_changed(
                    current_file, "".join(file_new), applied_files, diagnostics
                )
            current_file = Path(line.split(":", 1)[1].strip())
            mode = "update"
            file_original = None
            file_new = None
        elif line.startswith("*** Add File:"):
            if (
                current_file
                and mode == "update"
                and file_new is not None
                and not dry_run
            ):
                _write_if_changed(
                    current_file, "".join(file_new), applied_files, diagnostics
                )
            current_file = Path(line.split(":", 1)[1].strip())
            mode = "add"
            file_original = None
            file_new = []
        elif line.startswith("*** Begin Patch") or line.startswith("*** End Patch"):
            pass
        else:
            # Inside diff body
            if mode == "update" and current_file:
                # We rely on unified diff region markers; reconstruct by applying patch lines to original content
                if file_original is None:
                    try:
                        file_original = current_file.read_text(
                            encoding="utf-8", errors="replace"
                        )
                    except FileNotFoundError:
                        file_original = ""
                    file_new = file_original.splitlines(keepends=True)
                if line.startswith("@@"):
                    # we skip hunk headers directly (difflib context) - rely on +/- lines afterwards
                    pass
                elif line.startswith("+++") or line.startswith("---"):
                    pass
                elif line.startswith("+ ") or line.startswith("- "):
                    # improbable diff style with space after sign, treat as normal text
                    pass
                elif (
                    line.startswith("+")
                    and not line.startswith("+++ ")
                    and file_new is not None
                ):
                    file_new.append(
                        line[1:] + ("\n" if not line.endswith("\n") else "")
                    )
                elif (
                    line.startswith("-")
                    and not line.startswith("--- ")
                    and file_new is not None
                ):
                    # remove first matching line instance; naive but acceptable for Phase 0
                    for idx, existing in enumerate(list(file_new)):
                        if existing.rstrip("\n") == line[1:]:
                            del file_new[idx]
                            break
                else:
                    # context line
                    pass
            elif mode == "add" and current_file and file_new is not None:
                file_new.append(line + "\n")
        i += 1
    # Final write
    if (
        current_file
        and mode in {"update", "add"}
        and file_new is not None
        and not dry_run
    ):
        _write_if_changed(current_file, "".join(file_new), applied_files, diagnostics)

    rollback_token = None
    if applied_files:
        rollback_token = _make_rollback_token(applied_files)
    return PatchApplyResult(
        applied=not dry_run and bool(applied_files),
        diff=diff_text,
        dry_run=dry_run,
        rollback_token=rollback_token,
        diagnostics=diagnostics,
    )


def _write_if_changed(
    path: Path, new_content: str, applied: list[Path], diagnostics: list[str]
) -> None:
    path_parent = path.parent
    path_parent.mkdir(parents=True, exist_ok=True)
    old = ""
    try:
        old = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        pass
    if old != new_content:
        path.write_text(new_content, encoding="utf-8")
        applied.append(path)
        diagnostics.append(f"Updated {path}")
    else:
        diagnostics.append(f"No change for {path}")


def _make_rollback_token(files: list[Path]) -> str:
    h = hashlib.sha256()
    for p in files:
        h.update(p.as_posix().encode())
    return h.hexdigest()[:16]
