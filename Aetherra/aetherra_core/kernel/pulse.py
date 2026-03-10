# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors


class DriftAlert:
    def __init__(self, level: str = "info", message: str = ""):
        self.level = level
        self.message = message


class MemoryHealth:
    def __init__(self, score: float = 1.0, status: str = "healthy"):
        self.score = score
        self.status = status


class MemoryPulseMonitor:
    def __init__(self, db_path=None):
        self.db_path = db_path
        self._recent_alerts = []
        self._active_alerts = []
        self._last_health = MemoryHealth()

    def run_pulse_check(self, fragments, concept_clusters):
        fragment_count = len(fragments) if fragments is not None else 0
        cluster_count = len(concept_clusters) if concept_clusters is not None else 0
        score = 1.0 if fragment_count > 0 else 0.5
        status = "healthy" if score >= 0.8 else "degraded"
        self._last_health = MemoryHealth(score=score, status=status)

        if cluster_count == 0:
            alert = DriftAlert(
                level="warning", message="No concept clusters available during pulse check"
            )
            self._recent_alerts.append(alert)
            self._active_alerts = [alert]
        else:
            self._active_alerts = []

        return self._last_health

    def get_recent_alerts(self):
        return list(self._recent_alerts)

    def get_active_alerts(self):
        return list(self._active_alerts)

    def get_health_summary(self):
        return {
            "status": self._last_health.status,
            "score": self._last_health.score,
            "active_alerts": len(self._active_alerts),
            "recent_alerts": len(self._recent_alerts),
        }
