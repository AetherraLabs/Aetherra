"""
Shared memory graph optics: summarize memory nodes/edges for UI/Hub.

This provides a best-effort summary, even if no real memory engine exists.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    import sqlite3
except Exception:
    sqlite3 = None  # type: ignore


def summarize_memory_graph(max_nodes: int = 100) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Best-effort: if a GUI memory DB exists, sample some entries
    # Known default filenames in this repo
    candidates = [
        "gui_memory.db",
        "lyrixa_memory.db",
        "analytics_insights.db",
    ]
    for path in candidates:
        if sqlite3 is None:
            break
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            # Try common tables; ignore failures
            for table in ("memories", "nodes", "items"):
                try:
                    cur.execute(
                        f"SELECT rowid, * FROM {table} LIMIT ?",
                        (max_nodes - len(nodes),),
                    )
                    cols = [d[0] for d in cur.description]
                    for row in cur.fetchall():
                        nodes.append(
                            {
                                "source": path,
                                "table": table,
                                **{c: v for c, v in zip(["rowid"] + cols, row)},
                            }
                        )
                        if len(nodes) >= max_nodes:
                            break
                except Exception:
                    continue
                if len(nodes) >= max_nodes:
                    break
            conn.close()
        except Exception:
            continue

    return {
        "nodes_sample": nodes[:max_nodes],
        "edges_sample": edges,
        "nodes_count": len(nodes),
        "edges_count": len(edges),
        "sources": candidates,
    }
