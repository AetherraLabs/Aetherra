#!/usr/bin/env python3
"""Self-Model Manager

Loads, updates, and persists the system self-model. Provides atomic update helper and
coherence scoring stub. Lightweight; persistence is JSON file based for Phase 1.
"""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

# Local imports
from .schemas.self_model import (
    CapabilityDescriptor,
    IdentityProfile,
    ResourceProfile,
    SelfModel,
)

DEFAULT_SELF_MODEL_PATH = os.getenv("AETHERRA_SELF_MODEL_PATH", ".aetherra/self_model.json")
LOCK = threading.RLock()


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _self_model_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:self_model" and capability in {
        "consciousness:write",
        "identity:modify",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _evaluate_self_model_guardian(
    *,
    path: Path,
    before: SelfModel,
    after: SelfModel,
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:self_model"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    before_json = before.model_dump_json()
    after_json = after.model_dump_json()
    identity_changed = before.identity != after.identity
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="consciousness",
            action="consciousness.self_model_update",
            target="consciousness_self_model",
            purpose="Persist an updated consciousness self-model snapshot",
            capabilities=("consciousness:write", "identity:modify", "fs:write"),
            evidence=("self_model_manager.update",),
            reversible=True,
            rollback_plan="restore the previous self-model JSON snapshot from backup or version control",
            metadata={
                "path_hash": _hash_value(path.resolve()),
                "before_hash": _hash_value(before_json),
                "after_hash": _hash_value(after_json),
                "before_length": len(before_json),
                "after_length": len(after_json),
                "model_version": after.model_version,
                "identity_changed": identity_changed,
                "capability_count": len(after.capabilities),
                "anomaly_count": len(after.anomalies),
                "coherence_score": after.coherence_score,
            },
        ),
        approval_id=approval_id,
        capability_checker=_self_model_capability_checker,
    )


class SelfModelManager:
    def __init__(self, path: str = DEFAULT_SELF_MODEL_PATH):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._model: Optional[SelfModel] = None

    def load(self) -> SelfModel:
        with LOCK:
            if self._model is not None:
                return self._model
            if self._path.exists():
                try:
                    data = json.loads(self._path.read_text(encoding="utf-8"))
                    self._model = SelfModel(**data)
                except Exception:
                    # Corruption fallback: rebuild minimal model
                    self._model = self._bootstrap_minimal()
            else:
                self._model = self._bootstrap_minimal()
            return self._model

    def _bootstrap_minimal(self) -> SelfModel:
        identity = IdentityProfile(
            system_id=os.getenv("AETHERRA_SYSTEM_ID", "aetherra-node"),
            version=os.getenv("AETHERRA_VERSION", "dev"),
            deployment_tier=os.getenv("AETHERRA_DEPLOYMENT_TIER", "dev"),
        )
        capabilities = [CapabilityDescriptor(name="core", enabled=True, confidence=1.0)]
        resources = ResourceProfile(
            cpu_load=None,
            memory_used_mb=None,
            open_file_descriptors=None,
            processes=None,
        )
        return SelfModel(
            model_version=1,
            identity=identity,
            capabilities=capabilities,
            resources=resources,
            coherence_score=1.0,
        )

    def get(self) -> SelfModel:
        return self.load()

    def update(self, mutate: Callable[[SelfModel], None]) -> SelfModel:
        with LOCK:
            model = self.load()
            before = model.model_copy(deep=True)
            mutate(model)
            model.updated_at = datetime.utcnow()
            # Integration point: compute coherence score with richer signals
            if model.coherence_score < 0.5 and "low_coherence" not in model.anomalies:
                model.anomalies.append("low_coherence")
            guardian_decision = _evaluate_self_model_guardian(
                path=self._path,
                before=before,
                after=model,
            )
            if not guardian_decision.allowed:
                self._model = before
                raise PermissionError(f"guardian_denied:{guardian_decision.reason}")
            self._path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
            return model

    def set_resource_profile(
        self,
        cpu: float | None = None,
        mem_mb: float | None = None,
        fds: int | None = None,
        processes: int | None = None,
    ) -> None:
        def mutate(m: SelfModel):
            if cpu is not None:
                m.resources.cpu_load = cpu
            if mem_mb is not None:
                m.resources.memory_used_mb = mem_mb
            if fds is not None:
                m.resources.open_file_descriptors = fds
            if processes is not None:
                m.resources.processes = processes

        self.update(mutate)


SELF_MODEL_MANAGER_SINGLETON: Optional[SelfModelManager] = None


def get_self_model_manager() -> SelfModelManager:
    global SELF_MODEL_MANAGER_SINGLETON
    if SELF_MODEL_MANAGER_SINGLETON is None:
        SELF_MODEL_MANAGER_SINGLETON = SelfModelManager()
    return SELF_MODEL_MANAGER_SINGLETON
