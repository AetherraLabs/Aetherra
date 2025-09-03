import os
import sqlite3
from pathlib import Path

import pytest

from aetherra_persistent_memory import get_persistent_memory_system


@pytest.mark.asyncio
async def test_ownership_fact_seeded():
    # Ensure memory system is initialized (which seeds core facts)
    await get_persistent_memory_system()

    db = (
        Path(os.environ.get("AETHERRA_MEMORY_DIR", "aetherra_memory"))
        / "cognitive_memory.db"
    )
    assert db.exists(), "persistent memory DB should exist after init"

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute(
        """
        SELECT content, memory_type, verified FROM memories
        WHERE memory_type='fact' AND verified=1 AND content LIKE '%Aetherra Labs is founded and owned by%'
        LIMIT 1
        """
    )
    row = cur.fetchone()
    con.close()
    assert row is not None, "Ownership fact should be present and verified"
