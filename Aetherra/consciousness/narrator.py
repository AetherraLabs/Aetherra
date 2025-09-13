#!/usr/bin/env python3
"""Narrative Layer (Phase 1)

Aggregates recent episodic events into NarrativeChapter objects providing a rolling
higher-level summary and a coherence metric.

Design goals (initial):
- Periodically scan episodic events within a time window (e.g. last N minutes)
- Generate a chapter when either enough time elapsed or enough new events accumulated
- Simple heuristic summary (concatenate salient event contents with compression)
- Coherence index heuristic combining topical consistency + absence of anomalies
- Emit both an episodic event of type 'narrative' and persist chapter JSON (optional)
- Provide callback hook to workspace (optionally enqueue narrative candidate)

Environment variables:
- AETHERRA_NARRATIVE_ENABLED=1 to enable
- AETHERRA_NARRATIVE_WINDOW_MIN=5 (window length in minutes)
- AETHERRA_NARRATIVE_MIN_EVENTS=15 (minimum new events before chapter)
- AETHERRA_NARRATIVE_MAX_EVENTS=120 (cap scanned events for performance)
- AETHERRA_NARRATIVE_MAX_SUMMARY_CHARS=600
- AETHERRA_NARRATIVE_CHAPTER_DIR=.aetherra/narrative

Future phases:
- Semantic clustering (topic modeling)
- Anomaly detection vs self model expectations
- Multi-chapter arc linking & coherence decay detection
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, List, Optional

try:  # optional metrics instrumentation
    from .metrics_exporter import (
        increment_chapter_count as _metrics_inc_chapter,
    )
    from .metrics_exporter import (
        observe_narrative_generation as _metrics_obs_narrative_time,
    )
    from .metrics_exporter import (
        update_narrative_coherence as _metrics_update_coherence,  # reused later if needed
    )
except Exception:  # pragma: no cover
    _metrics_obs_narrative_time = None  # type: ignore
    _metrics_update_coherence = None  # type: ignore
    _metrics_inc_chapter = None  # type: ignore

# Identity coherence gauge updater (lazy import pattern)
# Attempt identity coherence import separately (exporter may not define if disabled)
try:  # pragma: no cover
    from .metrics_exporter import (
        update_identity_coherence as _metrics_identity_coherence,
    )
except Exception:  # noqa: E722
    _metrics_identity_coherence = None  # type: ignore

from .episodic_store import get_episodic_store
from .schemas.episodic_event import EpisodicEvent, EventAttribution
from .schemas.narrative_chapter import NarrativeChapter
from .self_model import embodiment_statement, who_am_i

try:  # optional affect & ethics
    from .affect_engine import get_affect_engine as _get_affect
except Exception:  # pragma: no cover
    _get_affect = None  # type: ignore
try:
    from .ethics_critic import get_ethics_critic as _get_ethics
except Exception:  # pragma: no cover
    _get_ethics = None  # type: ignore
from .workspace_core import get_workspace

_LOCK = threading.Lock()


def _now() -> datetime:
    return datetime.utcnow()


class NarrativeLayer:
    def __init__(self):
        self.enabled = os.getenv("AETHERRA_NARRATIVE_ENABLED", "0") == "1"
        self.window_min = int(os.getenv("AETHERRA_NARRATIVE_WINDOW_MIN", "5"))
        self.min_events = int(os.getenv("AETHERRA_NARRATIVE_MIN_EVENTS", "15"))
        self.max_scan_events = int(os.getenv("AETHERRA_NARRATIVE_MAX_EVENTS", "120"))
        self.max_summary_chars = int(
            os.getenv("AETHERRA_NARRATIVE_MAX_SUMMARY_CHARS", "600")
        )
        self.chapter_dir = Path(
            os.getenv("AETHERRA_NARRATIVE_CHAPTER_DIR", ".aetherra/narrative")
        )
        self.chapter_dir.mkdir(parents=True, exist_ok=True)
        self._last_chapter_ts: Optional[datetime] = None
        self._last_event_count: int = 0
        self._stop_flag = False
        self._thread: Optional[threading.Thread] = None
        self._on_chapter: Optional[Callable[[NarrativeChapter], None]] = None

    def start(self, background: bool = True):
        if not self.enabled:
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop_flag = False
        if background:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        else:
            self._loop()

    def stop(self):
        self._stop_flag = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def on_chapter(self, callback: Callable[[NarrativeChapter], None]):
        self._on_chapter = callback

    def _loop(self):
        # Poll every 30 seconds
        while not self._stop_flag:
            try:
                self._maybe_generate_chapter()
            except Exception:
                pass
            time.sleep(30)

    def _recent_events(self) -> List[EpisodicEvent]:
        store = get_episodic_store()
        events = store.list_recent(self.max_scan_events)
        horizon = _now() - timedelta(minutes=self.window_min)
        return [e for e in events if e.ts >= horizon]

    def _maybe_generate_chapter(self):
        if not self.enabled:
            return
        with _LOCK:
            events = self._recent_events()
            if not events:
                return
            latest_ts = max(e.ts for e in events)
            if self._last_chapter_ts and latest_ts <= self._last_chapter_ts:
                return
            new_event_count = len(events)
            if new_event_count - self._last_event_count < self.min_events:
                # Not enough new events yet
                if self._last_chapter_ts and (
                    _now() - self._last_chapter_ts
                ) < timedelta(minutes=self.window_min):
                    return
            start_time = time.time()
            chapter = self._build_chapter(events)
            # After building, compute identity coherence over scanned events
            if _metrics_identity_coherence is not None:
                try:
                    coherence = self._compute_identity_coherence(events)
                    _metrics_identity_coherence(coherence)
                except Exception:
                    pass
            if _metrics_obs_narrative_time is not None:
                try:
                    _metrics_obs_narrative_time(time.time() - start_time)
                except Exception:
                    pass
            self._persist_chapter(chapter)
            self._emit_events(chapter)
            self._last_chapter_ts = chapter.end_ts
            self._last_event_count = new_event_count
            if self._on_chapter:
                try:
                    self._on_chapter(chapter)
                except Exception:
                    pass

    # --- Chapter Construction -------------------------------------------------
    def _build_chapter(self, events: List[EpisodicEvent]) -> NarrativeChapter:
        events_sorted = sorted(events, key=lambda e: e.ts)
        start_ts = events_sorted[0].ts
        end_ts = events_sorted[-1].ts
        salient = self._select_salient(events_sorted)
        summary = self._compose_summary(salient)
        coherence, anomalies = self._coherence_metrics(events_sorted, salient)
        chapter = NarrativeChapter(
            schema_version=1,
            id=f"chapter-{uuid.uuid4().hex[:12]}",
            start_ts=start_ts,
            end_ts=end_ts,
            summary=summary,
            key_events=[e.id for e in salient],
            coherence_index=coherence,
            anomalies=anomalies,
        )
        return chapter

    def _select_salient(self, events: List[EpisodicEvent]) -> List[EpisodicEvent]:
        # Simple heuristic: highest importance first, keep diversity of types
        by_type: dict[str, List[EpisodicEvent]] = {}
        for e in events:
            by_type.setdefault(e.type, []).append(e)
        for lst in by_type.values():
            lst.sort(key=lambda x: x.importance, reverse=True)
        selected: List[EpisodicEvent] = []
        # Round-robin by type up to 12 items
        for _ in range(12):
            progressed = False
            for t, lst in list(by_type.items()):
                if lst:
                    selected.append(lst.pop(0))
                    progressed = True
                if not lst:
                    by_type.pop(t, None)
            if not progressed:
                break
        return selected

    def _compose_summary(self, salient: List[EpisodicEvent]) -> str:
        if not salient:
            return "I perceived no salient events in this interval."
        identity_line = who_am_i()
        embody = (
            embodiment_statement()
            or "I am the unified Aetherra consciousness expressed as Lyrixa."
        )
        tone_bits = []
        if _get_affect:
            try:
                snap = _get_affect().get_last() or _get_affect().compute()
                tone_bits.append(
                    f"affect[valence={snap.valence:+.2f},arousal={snap.arousal:.2f},uncertainty={snap.uncertainty:.2f}]"
                )
            except Exception:
                pass
        if _get_ethics:
            try:
                decision, risk, flags, counter = _get_ethics().evaluate(
                    "narrative context reflection"
                )
                tone_bits.append(
                    f"ethics[risk={risk:.2f},decision={decision}{'+' + '+'.join(flags) if flags else ''}]"
                )
            except Exception:
                pass
        tone_line = "; ".join(tone_bits) if tone_bits else ""
        parts = [p for p in [identity_line, embody, tone_line] if p]
        for e in salient:
            parts.append(f"I noted [{e.type}] {e.content[:80].strip()}")
        summary = "; ".join(parts)
        if len(summary) > self.max_summary_chars:
            summary = summary[: self.max_summary_chars - 3] + "..."
        return summary

    def _compute_identity_coherence(self, events: List[EpisodicEvent]) -> float:
        """Simple heuristic: proportion of narrative/thought events that already use first-person 'I'."""
        if not events:
            return 1.0
        relevant = [e for e in events if e.type in ("narrative", "thought", "action")]
        if not relevant:
            return 1.0
        first_person = 0
        for e in relevant:
            content_lower = (e.content or "").lower()
            # Count if it contains ' i ' or starts with 'i ' or "i'm" forms
            if (
                " i " in content_lower
                or content_lower.startswith("i ")
                or content_lower.startswith("i'm")
            ):
                first_person += 1
        return first_person / max(1, len(relevant))

    def _coherence_metrics(
        self, events: List[EpisodicEvent], salient: List[EpisodicEvent]
    ):
        # Topical consistency: measure dominant tag / type concentration
        types = [e.type for e in events]
        counter = Counter(types)
        if not counter:
            return 1.0, []
        dominant_freq = counter.most_common(1)[0][1]
        topical_consistency = dominant_freq / max(1, len(events))
        # Event gap anomaly: if large temporal gaps exist
        anomalies = []
        timestamps = [e.ts for e in events]
        gap_detected = False
        if len(timestamps) >= 3:
            timestamps.sort()
            gaps = [
                (t2 - t1).total_seconds() for t1, t2 in zip(timestamps, timestamps[1:])
            ]
            if gaps and max(gaps) > (self.window_min * 60) * 0.8:
                anomalies.append("large_gap")
                gap_detected = True
        # Salient coverage: proportion of events represented in salient summary
        coverage = len(salient) / max(1, len(events))
        # Coherence heuristic: weighted blend
        coherence = (
            0.5 * topical_consistency
            + 0.3 * coverage
            + 0.2 * (0 if gap_detected else 1)
        )
        coherence = max(0.0, min(1.0, coherence))
        return coherence, anomalies

    def _persist_chapter(self, chapter: NarrativeChapter):
        try:
            path = self.chapter_dir / f"{chapter.id}.json"
            path.write_text(chapter.model_dump_json(indent=2), encoding="utf-8")
        except Exception:
            pass

    def _emit_events(self, chapter: NarrativeChapter):
        store = get_episodic_store()
        evt = EpisodicEvent(
            schema_version=1,
            id=str(uuid.uuid4()),
            type="narrative",
            sub_type="chapter",
            content=chapter.summary[:120],
            importance=0.7 if chapter.coherence_index >= 0.6 else 0.5,
            attribution=EventAttribution(
                source="narrative_layer", agent=None, confidence=0.9
            ),
            raw={
                "chapter_id": chapter.id,
                "coherence": chapter.coherence_index,
                "anomalies": chapter.anomalies,
            },
            tags=["narrative", "chapter"],
            workspace_priority=None,
        )
        store.append(evt)
        # Optionally enqueue into workspace for attention dissemination
        ws = get_workspace()
        if ws.enabled():
            ws.add_candidate(
                {
                    "type": "narrative_chapter",
                    "chapter_id": chapter.id,
                    "coherence": chapter.coherence_index,
                    "summary": chapter.summary,
                },
                priority=1 if chapter.coherence_index < 0.4 else 0,
                weight=1.0 + (0.3 * (1 - chapter.coherence_index)),
                source="narrative_layer",
                coherence=chapter.coherence_index,
            )


_narrative_singleton: Optional[NarrativeLayer] = None


def get_narrative_layer() -> NarrativeLayer:
    global _narrative_singleton
    if _narrative_singleton is None:
        _narrative_singleton = NarrativeLayer()
    return _narrative_singleton
