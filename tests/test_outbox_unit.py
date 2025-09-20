# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import os


def test_outbox_enqueue_iter_clear(tmp_path):
    # Isolated outbox directory by changing cwd
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        # Aetherra imports
        from aetherra_outbox import Outbox

        ob = Outbox()
        e = ob.enqueue({"intent": "test", "value": 42})
        assert e.key and isinstance(e.key, str)
        lines = list(ob.iter_entries())
        assert len(lines) == 1
        assert lines[0]["payload"]["intent"] == "test"
        ob.clear()
        assert list(ob.iter_entries() or []) == []
    finally:
        os.chdir(old_cwd)
