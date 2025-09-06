# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Stub for SelfImprovementDashboard for modular self-improvement integration.
"""


class SelfImprovementDashboard:
    def __init__(self, *args, **kwargs):
        self.entries = []

    def add_entry(self, entry):
        self.entries.append(entry)

    def get_entries(self):
        return self.entries
