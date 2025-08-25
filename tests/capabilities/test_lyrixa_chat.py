#!/usr/bin/env python3
from pathlib import Path

import pytest

# Import the new LyrixaChatService
from Aetherra.lyrixa.chat.lyrixa_chat_service import ChatOptions, LyrixaChatService


@pytest.mark.asyncio
async def test_identity_and_awareness():
    svc = LyrixaChatService()
    await svc.initialize()

    # Identity checks
    resp1 = await svc.chat("Who is Lyrixa?", ChatOptions())
    assert isinstance(resp1.text, str)
    assert "Lyrixa" in resp1.text

    resp2 = await svc.chat("What is Aetherra?", ChatOptions())
    assert "AI Operating System" in resp2.text or "Operating System" in resp2.text

    resp3 = await svc.chat("Tell me about the workspace", ChatOptions())
    assert isinstance(resp3.awareness, dict)
    assert resp3.awareness.get("total_py_files", 0) > 0


@pytest.mark.asyncio
async def test_suggest_and_apply_conflict_fix(tmp_path: Path):
    # Create a temporary python file with conflict markers inside the repo
    repo_root = Path.cwd()
    conflict_file = repo_root / "tests" / "tmp_conflict.py"
    conflict_file.parent.mkdir(parents=True, exist_ok=True)

    conflict_contents = """# temp conflict file
<<<<<<< HEAD
print('left')
=======
print('right')
>>>>>>> branch
"""
    conflict_file.write_text(conflict_contents, encoding="utf-8")

    try:
        svc = LyrixaChatService()
        await svc.initialize()

        suggestions = await svc.suggest_fixes(limit=10)
        # Find our conflict suggestion
        target = None
        for s in suggestions:
            if (
                s.get("file") == str(conflict_file)
                and s.get("action") == "remove_conflict_markers"
            ):
                target = s
                break
        assert target is not None, (
            f"Expected suggestion for {conflict_file}, got: {suggestions}"
        )

        ok, change = await svc.apply_fix(target, edit_root=repo_root)
        assert ok, f"apply_fix failed: {change}"

        new_text = conflict_file.read_text(encoding="utf-8")
        assert (
            "<<<<<<<" not in new_text
            and ">>>>>>>" not in new_text
            and "=======" not in new_text
        )

    finally:
        # Cleanup
        try:
            conflict_file.unlink(missing_ok=True)
        except Exception:
            pass
