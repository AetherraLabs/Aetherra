# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

class DriftAlert:
    pass


class MemoryHealth:
    pass


class MemoryPulseMonitor:
    def __init__(self, db_path=None):
        pass

    def run_pulse_check(self, fragments, concept_clusters):
        return None

    def get_recent_alerts(self):
        return []

    def get_active_alerts(self):
        return []

    def get_health_summary(self):
        return None
